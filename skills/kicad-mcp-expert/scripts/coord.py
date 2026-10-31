#!/usr/bin/env python3
"""Convert coordinates between the two KiCad MCP servers.

`mcp__kicad__*` (kicad-claude-mcp) takes Y-UP millimetres and flips them using the
page height. `mcp__kicad-mixelpixx__*` and the .kicad_* files use KiCad-native Y-DOWN.
The flip is its own inverse: y' = page_height - y.

  coord.py to-kicad   X Y [--page A4 | --page-height 210 | --file board.kicad_pcb]
  coord.py to-mcp     X Y [...same]
  coord.py page       board.kicad_pcb        # print the page size the flip will use
"""
import argparse
import re
import sys

# Page heights exactly as kicad-claude-mcp computes them (adapters/pcb_editor.py and
# sch_editor.py `page_height_mm`): landscape height by paper name, `portrait` ignored,
# custom "User" sizes and US A-E sizes fall back to 210. This mirrors the server rather
# than KiCad's real page geometry, because the goal is to predict what the server will
# write. On a portrait or User-size sheet, `kicad` placement lands off by the
# difference, so prefer mixelpixx for placement there.
SERVER_PAGE_HEIGHTS = {
    "A0": 841.0, "A1": 594.0, "A2": 420.0, "A3": 297.0, "A4": 210.0, "A5": 148.0,
    "USLetter": 215.9, "USLegal": 215.9, "USLedger": 279.4,
}
DEFAULT_PAGE_HEIGHT = 210.0


def page_height_from_file(path: str) -> float:
    text = open(path, encoding="utf-8").read(20000)
    m = re.search(r'\(paper\s+"([^"]+)"([^)]*)\)', text)
    if not m:
        return DEFAULT_PAGE_HEIGHT
    name, rest = m.groups()
    h = SERVER_PAGE_HEIGHTS.get(name, DEFAULT_PAGE_HEIGHT)
    if "portrait" in rest or name not in SERVER_PAGE_HEIGHTS:
        print(f"warning: paper {name}{rest} is not handled by the kicad server's flip; "
              f"it will use {h:g} mm. Positions from `kicad` may be offset.", file=sys.stderr)
    return h


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["to-kicad", "to-mcp", "page"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--page", default=None)
    ap.add_argument("--page-height", type=float, default=None)
    ap.add_argument("--file", default=None)
    a = ap.parse_args()

    if a.cmd == "page":
        if not a.args:
            sys.exit("usage: coord.py page <file>")
        print(f"page height used for Y flip: {page_height_from_file(a.args[0])} mm")
        return
    if len(a.args) != 2:
        sys.exit("need X Y")
    x, y = map(float, a.args)
    if a.page_height is not None:
        h = a.page_height
    elif a.file:
        h = page_height_from_file(a.file)
    else:
        h = SERVER_PAGE_HEIGHTS.get(a.page or "A4", DEFAULT_PAGE_HEIGHT)
    print(f"{x:g} {h - y:g}   (page height {h:g} mm; {'Y-up -> Y-down' if a.cmd == 'to-kicad' else 'Y-down -> Y-up'})")


if __name__ == "__main__":
    main()
