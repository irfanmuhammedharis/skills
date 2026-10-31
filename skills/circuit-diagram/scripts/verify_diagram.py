#!/usr/bin/env python3
"""Verify a Fritzing-style breadboard SVG circuit diagram for precision errors.

Usage:
  python3 verify_diagram.py --svg diagram.svg [--spec wiring.json] [--code sketch.ino]

What it catches (this is the "without any mistake" gate):
  1. CLIPPED LABELS   - any <text> that would render outside the viewBox
  2. DANGLING WIRES   - a wire end that does not land on a pin, hole, rail,
                        or another wire end (junction)
  3. MISSING WIRES    - a connection listed in the spec with no matching wire
  4. ORPHAN REFS      - a spec reference (pin/hole/rail) that isn't in the SVG
  5. EXTRA WIRES      - wires in the SVG that the spec does not list (warning)
  6. CODE MISMATCH    - pin literals (D#, A#) in code that disagree with the spec

Spec format (wiring.json):
{
  "wires": [
    {"from": "D13", "to": "e1", "color": "#fb8c00", "note": "LED signal"},
    {"from": "f3", "to": "-rail", "color": "#37474f"},
    {"from": "-rail", "to": "GND", "color": "#37474f"}
  ],
  "labels": ["R1 220\u03a9", "LED1"]      // optional: component labels that must exist
}
Reference names: pins by id ("D13","A0","GND","GND2","GND3","5V","3V3","VIN","AREF","RESET"),
holes as "e1","f3" (row+col), rails as "-rail" and "+rail".

Exit code: 0 = pass, 1 = errors, 2 = warnings only.
"""
import argparse
import html
import json
import math
import pathlib
import re
import sys


def parse_path_points(d):
    """Return the vertex points of an SVG path (M/L/H/V/Q/T/Z), consuming all
    coordinate pairs per command so Q '400 580 46 228' yields its real end point."""
    tokens = re.findall(r"[MmLlHhVvQqTtZz]|-?[\d.]+(?:[eE][+-]?\d+)?", d)
    pts = []
    cur = None
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                continue
            if cmd in "Mm":
                while i < len(tokens) and not tokens[i].isalpha():
                    cur = (float(tokens[i]), float(tokens[i + 1])); i += 2
                    pts.append(cur)
            elif cmd in "Ll":
                while i < len(tokens) and not tokens[i].isalpha():
                    cur = (float(tokens[i]), float(tokens[i + 1])); i += 2
                    pts.append(cur)
            elif cmd in "Hh":
                while i < len(tokens) and not tokens[i].isalpha():
                    cur = (float(tokens[i]), cur[1]); i += 1
                    pts.append(cur)
            elif cmd in "Vv":
                while i < len(tokens) and not tokens[i].isalpha():
                    cur = (cur[0], float(tokens[i])); i += 1
                    pts.append(cur)
            elif cmd in "Qq":
                while i < len(tokens) and not tokens[i].isalpha():
                    i += 2  # control point (not a connection point)
                    cur = (float(tokens[i]), float(tokens[i + 1])); i += 2
                    pts.append(cur)
            elif cmd in "Tt":
                while i < len(tokens) and not tokens[i].isalpha():
                    cur = (float(tokens[i]), float(tokens[i + 1])); i += 2
                    pts.append(cur)
            else:
                break
        else:
            break
    return pts


def parse_svg(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    vb = re.search(r"viewBox=\"([-\d.\s]+)\"", text)
    view_box = [float(v) for v in vb.group(1).split()] if vb else None

    pins, holes, rails = {}, {}, {}
    texts = []
    wires = []

    for m in re.finditer(r'<g class="pin" id="pin-([^"]+)">.*?<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([-\d.]+)"', text):
        pins[m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(r'<circle class="hole" id="hole-([a-j])(\d+)" cx="([-\d.]+)" cy="([-\d.]+)" r="([-\d.]+)"', text):
        holes[m.group(1) + m.group(2)] = (float(m.group(3)), float(m.group(4)), float(m.group(5)))
    # rails: filled rects; red top = +rail, blue/gray bottom = -rail (multi-rect)
    rails = {"+rail": [], "-rail": []}
    for m in re.finditer(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"[^>]*fill="(#ff8a80|#90a4ae)"', text):
        x, y, w, h, fill = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5)
        name = "+rail" if fill == "#ff8a80" else "-rail"
        rails[name].append((x, y, x + w, y + h))
    for m in re.finditer(r'<line class="wire"[^>]*/>', text):
        tag = m.group(0)
        wires.append({"pts": [(float(re.search(r'x1="([-\d.]+)"', tag).group(1)), float(re.search(r'y1="([-\d.]+)"', tag).group(1))),
                              (float(re.search(r'x2="([-\d.]+)"', tag).group(1)), float(re.search(r'y2="([-\d.]+)"', tag).group(1)))],
                      "color": (re.search(r'stroke="(#[0-9a-fA-F]{6})"', tag) or [None, None])[1]})
    for m in re.finditer(r'<path class="wire"[^>]*>', text):
        tag = m.group(0)
        color = re.search(r'stroke="(#[0-9a-fA-F]{6})"', tag)
        d = re.search(r'd="([^"]+)"', tag)
        if d:
            wires.append({"pts": parse_path_points(d.group(1)),
                          "color": color.group(1) if color else None})
    for m in re.finditer(r'<text[^>]*x="([-\d.]+)" y="([-\d.]+)"[^>]*>([^<]+)</text>', text):
        attrs = m.group(0)
        size = float(re.search(r'font-size="([-\d.]+)"', attrs).group(1))
        texts.append({"x": float(m.group(1)), "y": float(m.group(2)),
                      "size": size, "content": html.unescape(m.group(3)),
                      "anchor": "end" if 'text-anchor="end"' in attrs else "middle" if 'text-anchor="middle"' in attrs else "start"})

    return {"view_box": view_box, "pins": pins, "holes": holes, "rails": rails,
            "texts": texts, "wires": wires}


def near(p, q, tol):
    return math.hypot(p[0] - q[0], p[1] - q[1]) <= tol


def point_in_rail(pt, rail):
    x0, y0, x1, y1 = rail
    return x0 - 2 <= pt[0] <= x1 + 2 and y0 - 2 <= pt[1] <= y1 + 2


def point_in_rails(pt, rects):
    return any(point_in_rail(pt, r) for r in rects)


def check_clipped_labels(svg, tol=8.0):
    errs = []
    if not svg["view_box"]:
        return errs
    vx, vy, vw, vh = svg["view_box"]
    for t in svg["texts"]:
        w = 0.6 * t["size"] * len(t["content"])   # rough width estimate
        h = t["size"] * 1.4
        if t["anchor"] == "middle":
            x0, x1 = t["x"] - w / 2, t["x"] + w / 2
        elif t["anchor"] == "end":
            x0, x1 = t["x"] - w, t["x"]
        else:
            x0, x1 = t["x"], t["x"] + w
        y0, y1 = t["y"] - t["size"], t["y"] + 2
        if x0 < vx - tol or x1 > vx + vw + tol or y0 < vy - tol or y1 > vy + vh + tol:
            errs.append(f'  label "{t["content"]}" at ({t["x"]:.0f},{t["y"]:.0f}) may be clipped '
                        f'(bbox {x0:.0f},{y0:.0f}-{x1:.0f},{y1:.0f}, viewBox {vx:.0f},{vy:.0f}-{vx+vw:.0f},{vy+vh:.0f})')
    return errs


def check_dangling_wires(svg, tol=5.0):
    errs = []
    targets = list(svg["pins"].values()) + list(svg["holes"].values())
    rail_list = [r for rects in svg["rails"].values() for r in rects]
    # terminals = first + last point of every wire (junctions)
    terminals = []
    for w in svg["wires"]:
        if len(w["pts"]) >= 1:
            terminals.append(w["pts"][0])
            terminals.append(w["pts"][-1])
    for w in svg["wires"]:
        for pt in (w["pts"][0], w["pts"][-1]):
            on_target = any(near(pt, t[:2], tol) for t in targets) or \
                        any(point_in_rail(pt, r) for r in rail_list) or \
                        any(near(pt, q, 1.5) for q in terminals if q != pt)
            if not on_target:
                errs.append(f"  wire end ({pt[0]:.0f},{pt[1]:.0f}) dangles - not on any pin, hole, rail or junction")
    return errs


def build_coord_map(svg):
    cm = {}
    for name, (x, y, _r) in svg["pins"].items():
        cm[name] = (x, y)
    for name, (x, y, _r) in svg["holes"].items():
        cm[name] = (x, y)
    return cm


def check_spec(svg, spec, tol=6.0):
    errs, warns = [], []
    cm = build_coord_map(svg)

    for conn in spec.get("wires", []):
        frm, to, col = conn["from"], conn["to"], conn.get("color")
        note = conn.get("note", "")
        for ref in (frm, to):
            if ref in cm or (ref in ("-rail", "+rail") and ref in svg["rails"]):
                continue
            errs.append(f'  spec ref "{ref}" not found in SVG (missing pin/hole/rail)')
        if frm in cm and to in cm:
            pa, pb = cm[frm], cm[to]
            found = False
            for w in svg["wires"]:
                a, b = w["pts"][0], w["pts"][-1]
                match = (near(a, pa, tol) and near(b, pb, tol)) or \
                        (near(a, pb, tol) and near(b, pa, tol))
                if match:
                    if col and w["color"] and w["color"].lower() != col.lower():
                        warns.append(f'  wire {frm}->{to}: color is {w["color"]}, spec says {col}')
                    found = True
                    break
            if not found:
                errs.append(f'  missing wire: {frm} -> {to} {note}')
        elif frm in cm and to in ("-rail", "+rail"):
            pa = cm[frm]
            rects = svg["rails"][to]
            found = any((near(w["pts"][-1], pa, tol) and point_in_rails(w["pts"][0], rects)) or
                        (near(w["pts"][0], pa, tol) and point_in_rails(w["pts"][-1], rects))
                        for w in svg["wires"])
            if not found:
                errs.append(f'  missing wire: {frm} -> {to} {note}')
        elif to in cm and frm in ("-rail", "+rail"):
            pa = cm[to]
            rects = svg["rails"][frm]
            found = any((near(w["pts"][-1], pa, tol) and point_in_rails(w["pts"][0], rects)) or
                        (near(w["pts"][0], pa, tol) and point_in_rails(w["pts"][-1], rects))
                        for w in svg["wires"])
            if not found:
                errs.append(f'  missing wire: {frm} -> {to} {note}')

    for lab in spec.get("labels", []):
        all_text = " ".join(t["content"] for t in svg["texts"])
        if lab not in all_text:
            errs.append(f'  missing component label "{lab}"')

    # extra wires not in the spec (informational)
    covered = set()
    for conn in spec.get("wires", []):
        covered.add(frozenset((conn["from"], conn["to"])))
    for w in svg["wires"]:
        a, b = w["pts"][0], w["pts"][-1]
        refs = [n for n, c in cm.items() if near(a, c, 6.0)] + \
               [n for n, c in cm.items() if near(b, c, 6.0)]
        rail_refs = [r for r in svg["rails"] if point_in_rails(a, svg["rails"][r]) or point_in_rails(b, svg["rails"][r])]
        key = frozenset(refs + rail_refs)
        if len(key) == 2 and key not in covered:
            warns.append(f'  wire in SVG not listed in spec: {sorted(key)}')
    return errs, warns


def extract_code_pins(code):
    """Heuristic: collect pins referenced in an Arduino sketch.
    Strips comments, then catches 'D13'/'A0' literals, literal args to pin APIs,
    and 'int <..pin..> = N;' assignments."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    pins = set(re.findall(r"\b([AD]\d{1,2})\b", code))
    pins |= set(re.findall(r"pinMode\((\d+)", code))
    pins |= set(re.findall(r"digital(?:Read|Write)\((\d+)", code))
    pins |= set(re.findall(r"analog(?:Read|Write)\((\d+)", code))
    pins |= set(re.findall(r"tone\((\d+)", code))
    pins |= set(v for _, v in re.findall(r"(?i)\b(\w*pin\w*)\s*=\s*(\d+)", code))
    return pins


def spec_pin_refs(spec):
    """Normalize spec pin refs: D13 -> '13', A0 -> 'A0', plain numbers kept."""
    refs = set()
    for c in spec.get("wires", []):
        for r in (c["from"], c["to"]):
            if re.fullmatch(r"D\d{1,2}", r):
                refs.add(r[1:])
            elif re.fullmatch(r"A\d{1,2}", r):
                refs.add(r)
            elif r.isdigit():
                refs.add(r)
    return refs


def check_code(spec, code_path):
    e, w = [], []
    code = pathlib.Path(code_path).read_text(encoding="utf-8")
    code_pins = extract_code_pins(code)
    spec_refs = spec_pin_refs(spec)
    for p in sorted(code_pins):
        if p not in spec_refs:
            e.append(f'  code uses pin {p} but the wiring spec does not')
    for p in sorted(spec_refs):
        if p not in code_pins:
            w.append(f'  spec wires pin {p} but code never uses it (may be intentional)')
    return e, w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg", required=True)
    ap.add_argument("--spec")
    ap.add_argument("--code")
    ap.add_argument("--tolerance", type=float, default=6.0)
    args = ap.parse_args()

    svg = parse_svg(args.svg)
    errors, warnings = [], []

    print(f"== {args.svg} ==")
    print(f"pins={len(svg['pins'])} holes={len(svg['holes'])} wires={len(svg['wires'])}")

    clipped = check_clipped_labels(svg)
    errors += clipped
    print(f"[clipped labels] {len(clipped)} found")

    dangling = check_dangling_wires(svg, args.tolerance)
    errors += dangling
    print(f"[dangling wires] {len(dangling)} found")

    spec = None
    if args.spec:
        spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
        e, w = check_spec(svg, spec, args.tolerance)
        errors += e
        warnings += w
        print(f"[spec check] {len(e)} errors, {len(w)} warnings")
        for x in e + w:
            print(x)

    if args.code and spec:
        e, w = check_code(spec, args.code)
        errors += e
        warnings += w
        print(f"[code check] {len(e)} errors, {len(w)} warnings")
        for x in e + w:
            print(x)

    for x in clipped + dangling:
        print(x)

    print("-" * 40)
    if errors:
        print(f"RESULT: FAIL ({len(errors)} error(s))")
        return 1
    if warnings:
        print(f"RESULT: PASS with {len(warnings)} warning(s)")
        return 2
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
