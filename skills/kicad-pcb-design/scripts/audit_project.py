#!/usr/bin/env python3
"""
audit_project.py - static pre-fabrication audit of a KiCad project.

    python3 audit_project.py <project-dir-or-.kicad_pcb> [--profile jlcpcb] [--json out.json]

Reads the .kicad_sch and .kicad_pcb files directly (no KiCad installation needed) and
reports the things that are cheap to get wrong and expensive to discover at assembly:
geometry below the fab's floor, missing BOM data, footprints that will fall out of the
position file, schematic/board reference mismatches, unfilled zones, silkscreen that
cannot be printed.

This complements DRC and ERC. It does not replace them - run
`kicad-cli pcb drc --schematic-parity` before every release.

Exit code 1 if any FAIL was reported, otherwise 0.
"""

import argparse
import json
import math
import os
import re
import sys

# fab profiles: all values in mm
PROFILES = {
    "generic": dict(track=0.15, clearance=0.15, drill=0.30, via=0.45, annular=0.13,
                    silk_width=0.15, silk_height=0.8, edge=0.25),
    "jlcpcb": dict(track=0.127, clearance=0.127, drill=0.30, via=0.45, annular=0.13,
                   silk_width=0.15, silk_height=0.8, edge=0.20),
    "pcbway": dict(track=0.127, clearance=0.127, drill=0.30, via=0.45, annular=0.13,
                   silk_width=0.15, silk_height=0.8, edge=0.20),
}

FINDINGS = []


def report(level, section, message):
    FINDINGS.append({"level": level, "section": section, "message": message})


# --------------------------------------------------------------- S-expressions
TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+')


def parse_sexpr(text):
    """Parse an S-expression file into nested lists. Strings keep their value."""
    stack, cur = [], []
    for tok in TOKEN.findall(text):
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            if not stack:
                continue
            parent = stack.pop()
            parent.append(cur)
            cur = parent
        elif tok.startswith('"'):
            cur.append(tok[1:-1].replace('\\"', '"').replace("\\\\", "\\"))
        else:
            cur.append(tok)
    return cur


def find_all(node, tag):
    """Yield every sub-list whose head is `tag`, at any depth."""
    if isinstance(node, list):
        if node and node[0] == tag:
            yield node
        for child in node:
            if isinstance(child, list):
                yield from find_all(child, tag)


def find_first(node, tag):
    return next(find_all(node, tag), None)


def get(node, tag, default=None):
    """Value of the first (tag value) pair directly inside node."""
    for child in node:
        if isinstance(child, list) and child and child[0] == tag and len(child) > 1:
            return child[1]
    return default


def num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# --------------------------------------------------------------- board audit
def audit_pcb(path, prof, data):
    src = open(path, encoding="utf-8", errors="replace").read()
    root = parse_sexpr(src)
    pcb = root[0] if root and root[0] and root[0][0] == "kicad_pcb" else root

    data["pcb_file"] = os.path.basename(path)
    data["format_version"] = get(pcb, "version")
    data["generator_version"] = get(pcb, "generator_version")

    # ---- layers
    layers = find_first(pcb, "layers")
    copper = []
    if layers:
        for entry in layers[1:]:
            if isinstance(entry, list) and len(entry) > 2 and str(entry[1]).endswith(".Cu"):
                copper.append(entry[1])
    data["copper_layers"] = copper
    report("INFO", "stackup", f"{len(copper)} copper layers: {', '.join(copper) or 'unknown'}")

    stack = find_first(pcb, "stackup")
    if stack:
        thick = sum(num(get(l, "thickness")) for l in find_all(stack, "layer"))
        data["stackup_thickness_mm"] = round(thick, 3)
        report("INFO", "stackup", f"stackup total thickness {thick:.2f} mm")
    else:
        report("WARN", "stackup", "no physical stackup defined - impedance, 3D export and "
                                  "time-domain tuning all depend on it")

    # ---- board outline
    edge_pts, open_ends = [], 0
    seg_ends = []
    for tag in ("gr_line", "gr_arc", "gr_rect", "gr_poly", "gr_circle"):
        for item in find_all(pcb, tag):
            if get(item, "layer") != "Edge.Cuts":
                continue
            pts = []
            for key in ("start", "end", "center", "mid"):
                node = find_first(item, key)
                if node and len(node) >= 3:
                    pts.append((num(node[1]), num(node[2])))
            poly = find_first(item, "pts")
            if poly:
                for xy in find_all(poly, "xy"):
                    pts.append((num(xy[1]), num(xy[2])))
            edge_pts += pts
            if tag == "gr_line" and len(pts) == 2:
                seg_ends += pts
    if not edge_pts:
        report("FAIL", "outline", "no geometry on Edge.Cuts - the fab has no board shape")
    else:
        xs = [p[0] for p in edge_pts]
        ys = [p[1] for p in edge_pts]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        data["board_size_mm"] = [round(w, 2), round(h, 2)]
        report("INFO", "outline", f"board extents {w:.1f} x {h:.1f} mm")
        # every line endpoint should be shared with another segment endpoint
        for pt in seg_ends:
            matches = sum(1 for q in seg_ends
                          if math.hypot(pt[0] - q[0], pt[1] - q[1]) < 0.01)
            if matches < 2:
                open_ends += 1
        if open_ends:
            report("FAIL", "outline",
                   f"{open_ends} Edge.Cuts line endpoint(s) do not meet another segment - "
                   "the outline is probably not a closed loop")

    # ---- tracks
    widths, track_count = [], 0
    for seg in list(find_all(pcb, "segment")) + list(find_all(pcb, "arc")):
        wv = get(seg, "width")
        if wv is not None:
            widths.append(num(wv))
            track_count += 1
    data["track_count"] = track_count
    if track_count == 0:
        report("FAIL", "routing", "no tracks on the board - is this the right file?")
    else:
        mn = min(widths)
        data["min_track_mm"] = round(mn, 4)
        level = "FAIL" if mn < prof["track"] - 1e-9 else "INFO"
        report(level, "routing",
               f"{track_count} track segments, narrowest {mn:.3f} mm "
               f"(profile floor {prof['track']:.3f} mm)")

    # ---- vias
    drills, sizes, annulars = [], [], []
    for via in find_all(pcb, "via"):
        s, d = num(get(via, "size")), num(get(via, "drill"))
        if s and d:
            sizes.append(s)
            drills.append(d)
            annulars.append((s - d) / 2)
    data["via_count"] = len(drills)
    if drills:
        report("INFO" if min(drills) >= prof["drill"] else "FAIL", "vias",
               f"{len(drills)} vias, smallest drill {min(drills):.3f} mm "
               f"(floor {prof['drill']:.3f} mm)")
        report("INFO" if min(annulars) >= prof["annular"] else "FAIL", "vias",
               f"smallest annular ring {min(annulars):.3f} mm "
               f"(floor {prof['annular']:.3f} mm)")
    else:
        report("WARN", "vias", "no vias found - expected on any multi-layer board")

    # ---- zones
    zones = list(find_all(pcb, "zone"))
    filled = sum(1 for z in zones if find_first(z, "filled_polygon"))
    data["zone_count"] = len(zones)
    if zones:
        level = "INFO" if filled == len(zones) else "FAIL"
        report(level, "zones", f"{len(zones)} zones, {filled} carry a fill "
                               "(unfilled zones export as empty copper)")
    else:
        report("WARN", "zones", "no copper zones - most designs want at least a ground pour")

    # ---- footprints
    refs, no_model, dnp, unspecified, smd, tht = [], [], [], [], 0, 0
    for fp in find_all(pcb, "footprint"):
        ref = None
        for prop in find_all(fp, "property"):
            if len(prop) > 2 and prop[1] == "Reference":
                ref = prop[2]
        ref = ref or "?"
        refs.append(ref)
        attrs = find_first(fp, "attr") or []
        flat = " ".join(str(x) for x in attrs)
        if "smd" in flat:
            smd += 1
        elif "through_hole" in flat:
            tht += 1
        else:
            unspecified.append(ref)
        if "dnp" in flat:
            dnp.append(ref)
        if not find_first(fp, "model"):
            no_model.append(ref)
    data["footprints"] = len(refs)
    data["refs_pcb"] = sorted(refs)
    report("INFO", "footprints",
           f"{len(refs)} footprints: {smd} SMD, {tht} through-hole, "
           f"{len(unspecified)} unspecified type, {len(dnp)} marked DNP")
    if unspecified:
        report("WARN", "footprints",
               "footprints with no SMD/through-hole attribute are dropped from the position "
               f"file: {', '.join(sorted(unspecified)[:12])}"
               f"{' ...' if len(unspecified) > 12 else ''}")
    if no_model:
        report("WARN", "footprints",
               f"{len(no_model)} footprints have no 3D model - the STEP export and the "
               "enclosure fit check will be incomplete")
    dupes = {r for r in refs if refs.count(r) > 1 and r != "?"}
    if dupes:
        report("FAIL", "footprints", f"duplicate references on the board: {', '.join(sorted(dupes))}")

    # ---- silkscreen legibility
    small_text = 0
    for tag in ("fp_text", "gr_text", "property"):
        for t in find_all(pcb, tag):
            layer = get(t, "layer") or ""
            if "SilkS" not in str(layer):
                continue
            eff = find_first(t, "effects")
            size = find_first(eff, "size") if eff else None
            if size and len(size) >= 3 and num(size[1]) < prof["silk_height"] - 1e-9:
                small_text += 1
    if small_text:
        report("WARN", "silkscreen",
               f"{small_text} silkscreen text item(s) below {prof['silk_height']} mm height - "
               "may not be printed legibly")

    # ---- test points / fiducials by name
    tp = [r for r in refs if re.match(r"^(TP|FID)", r, re.I)]
    if not tp:
        report("WARN", "test", "no TP*/FID* references found - add test points for bring-up "
                               "and fiducials if the board is machine-assembled")
    else:
        report("INFO", "test", f"{len(tp)} test point / fiducial references: {', '.join(sorted(tp)[:10])}")


# --------------------------------------------------------------- schematic audit
def audit_sch(paths, data):
    refs, missing_fp, missing_mpn, bad_value, dnp = [], [], [], [], []
    for path in paths:
        src = open(path, encoding="utf-8", errors="replace").read()
        root = parse_sexpr(src)
        sch = root[0] if root and root[0] and root[0][0] == "kicad_sch" else root
        for sym in find_all(sch, "symbol"):
            lib_id = get(sym, "lib_id")
            if not lib_id or not find_first(sym, "at"):
                continue                      # lib_symbols definition, not an instance
            props = {}
            for prop in find_all(sym, "property"):
                if len(prop) > 2:
                    props[prop[1]] = prop[2]
            ref = props.get("Reference", "?")
            if ref.startswith("#") or lib_id.startswith("power:"):
                continue                      # power symbols and other virtual parts
            refs.append(ref)
            if not props.get("Footprint"):
                missing_fp.append(ref)
            if not any(props.get(k) for k in ("MPN", "LCSC", "Manufacturer Part Number",
                                              "Part Number", "Mfr. No")):
                missing_mpn.append(ref)
            val = (props.get("Value") or "").strip()
            if val in ("", "~", "Value"):
                bad_value.append(ref)
            if "dnp" in " ".join(str(x) for x in (find_first(sym, "dnp") or [])):
                dnp.append(ref)

    data["refs_sch"] = sorted(set(refs))
    report("INFO", "schematic",
           f"{len(set(refs))} placed symbols across {len(paths)} sheet(s)")
    if missing_fp:
        report("FAIL", "schematic",
               f"{len(missing_fp)} symbol(s) with no footprint assigned: "
               f"{', '.join(sorted(set(missing_fp))[:12])}")
    if bad_value:
        report("WARN", "schematic",
               f"{len(bad_value)} symbol(s) with an empty or placeholder Value: "
               f"{', '.join(sorted(set(bad_value))[:12])}")
    if missing_mpn:
        report("WARN", "bom",
               f"{len(missing_mpn)} symbol(s) without MPN/supplier part number - purchasing "
               f"and assembly will guess: {', '.join(sorted(set(missing_mpn))[:12])}"
               f"{' ...' if len(missing_mpn) > 12 else ''}")
    unannotated = [r for r in refs if r.endswith("?")]
    if unannotated:
        report("FAIL", "schematic", f"{len(unannotated)} unannotated reference(s)")


def cross_check(data):
    sch = set(data.get("refs_sch", []))
    pcb = set(r for r in data.get("refs_pcb", []) if r != "?")
    if not sch or not pcb:
        return
    only_sch = sorted(sch - pcb)
    only_pcb = sorted(pcb - sch)
    if only_sch:
        report("FAIL", "parity",
               f"in schematic but not on the board: {', '.join(only_sch[:15])}"
               f"{' ...' if len(only_sch) > 15 else ''}")
    if only_pcb:
        report("WARN", "parity",
               f"on the board but not in the schematic (mechanical parts are fine here): "
               f"{', '.join(only_pcb[:15])}{' ...' if len(only_pcb) > 15 else ''}")
    if not only_sch and not only_pcb:
        report("INFO", "parity", f"all {len(sch)} references match between schematic and board")


# --------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Static pre-fabrication audit of a KiCad project")
    ap.add_argument("target", help="project directory or .kicad_pcb file")
    ap.add_argument("--profile", default="generic", choices=sorted(PROFILES))
    ap.add_argument("--json", help="also write the findings to this JSON file")
    args = ap.parse_args()

    prof = PROFILES[args.profile]
    if os.path.isdir(args.target):
        pcbs = [os.path.join(args.target, f) for f in sorted(os.listdir(args.target))
                if f.endswith(".kicad_pcb")]
        schs = [os.path.join(args.target, f) for f in sorted(os.listdir(args.target))
                if f.endswith(".kicad_sch")]
        for sub in ("sheets", "hardware"):
            d = os.path.join(args.target, sub)
            if os.path.isdir(d):
                schs += [os.path.join(d, f) for f in sorted(os.listdir(d))
                         if f.endswith(".kicad_sch")]
    else:
        pcbs = [args.target]
        schs = [args.target[:-len(".kicad_pcb")] + ".kicad_sch"]
        schs = [p for p in schs if os.path.exists(p)]

    if not pcbs:
        print(f"error: no .kicad_pcb found in {args.target}", file=sys.stderr)
        return 2

    data = {"profile": args.profile}
    print(f"KiCad project audit  (fab profile: {args.profile})")
    print("=" * 72)

    if schs:
        audit_sch(schs, data)
    else:
        report("WARN", "schematic", "no schematic found - board audited on its own")
    audit_pcb(pcbs[0], prof, data)
    cross_check(data)

    order = {"FAIL": 0, "WARN": 1, "INFO": 2}
    for level in ("FAIL", "WARN", "INFO"):
        items = [f for f in FINDINGS if f["level"] == level]
        if not items:
            continue
        print(f"\n-- {level} ({len(items)}) " + "-" * (60 - len(level)))
        for f in items:
            print(f"  [{f['section']}] {f['message']}")

    fails = sum(1 for f in FINDINGS if f["level"] == "FAIL")
    warns = sum(1 for f in FINDINGS if f["level"] == "WARN")
    print("\n" + "=" * 72)
    print(f"{fails} fail, {warns} warn. This audit is not a substitute for "
          "`kicad-cli pcb drc --schematic-parity`.")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"summary": data,
                       "findings": sorted(FINDINGS, key=lambda f: order[f["level"]])},
                      fh, indent=2)
        print(f"findings written to {args.json}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
