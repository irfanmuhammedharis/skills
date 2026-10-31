#!/usr/bin/env python3
"""Check a schematic's real netlist (kicad-cli) against a connection spec.

A batch tool saying "connected 12 pins" is a claim; this is the evidence. It also checks the
negative cases (things that must NOT be joined), which is where wiring mistakes hide.

  netlist_check.py <root.kicad_sch> <spec.json>

spec.json:
  {
    "same":  [["Q1.3", "BT1.2", "Q1 emitter on 0 V"], ["R4.2", "Q1.2", "R4 feeds Q1 base"]],
    "apart": [["Q1.2", "Q2.2", "bases are separate"]],
    "values": {"R1": "1k", "Q1": "BC547"}
  }
Pins are REF.PIN using the symbol's pin NUMBER (check with list_symbol_pins first; for a
BC547, 1=C 2=B 3=E). The third item of each pair is the label printed in the report.
Exit 1 if anything fails.
"""
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def load(sch: str):
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "n.xml"
        r = subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadxml",
                            "-o", str(out), sch], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"kicad-cli cannot load {sch}: {(r.stderr or r.stdout).strip()}\n"
                     "A tool edit probably wrote something invalid (see gotchas-recovery.md).")
        root = ET.parse(out).getroot()
    pin2net = {}
    for net in root.iter("net"):
        for n in net.iter("node"):
            pin2net[f"{n.get('ref')}.{n.get('pin')}"] = net.get("name")
    values = {c.get("ref"): c.findtext("value") for c in root.iter("comp")}
    return pin2net, values


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pin2net, values = load(sys.argv[1])
    spec = json.loads(Path(sys.argv[2]).read_text())
    fails = 0

    def report(ok, why, detail):
        nonlocal fails
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {why:<60} {detail}")

    for a, b, why in spec.get("same", []):
        na, nb = pin2net.get(a), pin2net.get(b)
        report(na is not None and na == nb, why, f"[{a} ~ {b}] {na if na == nb else f'{na} vs {nb}'}")
    for a, b, why in spec.get("apart", []):
        na, nb = pin2net.get(a), pin2net.get(b)
        report(na != nb or na is None, why, f"[{a} !~ {b}]")
    for ref, want in spec.get("values", {}).items():
        report(values.get(ref) == want, f"{ref} value is {want}", f"(found {values.get(ref)})")
    print(f"\nRESULT: {'ALL CHECKS PASSED' if not fails else f'{fails} CHECK(S) FAILED'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
