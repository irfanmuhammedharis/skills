#!/usr/bin/env python3
"""Golden-netlist snapshot/compare for KiCad schematics, via kicad-cli.

Proves that a cosmetic pass (lint, snap, field autoplace) changed no connectivity,
or that an ECO changed exactly the intended nets.

  netlist_diff.py snapshot <root.kicad_sch> <out.json>
  netlist_diff.py compare  <root.kicad_sch> <golden.json>   # exit 1 on any drift
  netlist_diff.py show     <root.kicad_sch>                 # print NET: REF.PIN ...

Nets are compared by their pin sets, so a net that was only renamed is reported as a
rename, not as a remove + add.
"""
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def export_nets(sch: str) -> dict[str, list[str]]:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "net.xml"
        r = subprocess.run(
            ["kicad-cli", "sch", "export", "netlist", "--format", "kicadxml", "-o", str(out), sch],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not out.exists():
            sys.exit(f"kicad-cli netlist export failed:\n{r.stderr or r.stdout}")
        root = ET.parse(out).getroot()
    nets: dict[str, list[str]] = {}
    for net in root.iter("net"):
        pins = sorted(f"{n.get('ref')}.{n.get('pin')}" for n in net.iter("node"))
        nets[net.get("name")] = pins
    return nets


def compare(golden: dict, current: dict) -> int:
    g_by_pins = {tuple(v): k for k, v in golden.items()}
    c_by_pins = {tuple(v): k for k, v in current.items()}
    renamed = [(g_by_pins[p], c_by_pins[p]) for p in g_by_pins
               if p in c_by_pins and g_by_pins[p] != c_by_pins[p]]
    renamed_old = {a for a, _ in renamed}
    renamed_new = {b for _, b in renamed}
    removed = [n for n in golden if n not in current and n not in renamed_old]
    added = [n for n in current if n not in golden and n not in renamed_new]
    changed = [n for n in golden if n in current and golden[n] != current[n]]

    for a, b in renamed:
        print(f"RENAMED  {a} -> {b}")
    for n in removed:
        print(f"REMOVED  {n}: {' '.join(golden[n])}")
    for n in added:
        print(f"ADDED    {n}: {' '.join(current[n])}")
    for n in changed:
        g, c = set(golden[n]), set(current[n])
        print(f"CHANGED  {n}: +{sorted(c - g)} -{sorted(g - c)}")
    drift = len(renamed) + len(removed) + len(added) + len(changed)
    print(f"\n{len(golden)} nets before, {len(current)} after, {drift} difference(s)")
    return 1 if drift else 0


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in {"snapshot", "compare", "show"}:
        sys.exit(__doc__)
    cmd, sch = sys.argv[1], sys.argv[2]
    nets = export_nets(sch)
    if cmd == "show":
        for n in sorted(nets):
            print(f"{n}: {' '.join(nets[n])}")
    elif cmd == "snapshot":
        Path(sys.argv[3]).write_text(json.dumps(nets, indent=1, sort_keys=True))
        print(f"saved {len(nets)} nets -> {sys.argv[3]}")
    else:
        sys.exit(compare(json.loads(Path(sys.argv[3]).read_text()), nets))


if __name__ == "__main__":
    main()
