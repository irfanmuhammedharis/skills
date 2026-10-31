---
name: kicad-pcb-design
description: "Elite-level PCB design in KiCad 10/9, schematic to fabrication: project and library setup, schematic capture and ERC, board setup and stackup, custom design rules (.kicad_dru), placement, routing, copper pours, controlled impedance, length and time-domain tuning, DFM review, and manufacturing outputs (Gerber, drill, BOM, CPL, STEP, IPC-2581, ODB++) through kicad-cli. Use WHENEVER a PCB is being designed, reviewed, or released, and whenever KiCad, Eeschema, pcbnew, gerbers, footprints, symbols, netclasses, DRC/ERC, stackups, JLCPCB/PCBWay output, panelization, or assembly data come up. Trigger on 'design a PCB for X', 'lay out this board', 'route this', 'why is DRC complaining', 'write a design rule', 'make a footprint', 'what stackup for 50 ohms', 'generate the gerbers/BOM/CPL', 'review my board before I order it' - even when KiCad is never named, and even when the input is only a rough product idea. Also for KiCad automation: kicad-cli scripting, CI design checks, jobsets, and the kipy IPC API."
---

# KiCad PCB Design

Design boards that come back from the fab working, assemble without rework, and can be
rebuilt identically in two years. An elite designer's advantage is not routing speed — it is
that constraints are encoded in the tool before the first track is placed, so the design
cannot silently drift out of manufacturability, and every claim (impedance, current, thermal,
timing) is backed by a number.

Assume **KiCad 10** (current stable, released March 2026) unless the user says otherwise;
see [references/automation-scripting.md](references/automation-scripting.md) §1 for version
differences that change commands. Check with `kicad-cli version`.

## Operating rules

- **Constraints first, copper second.** Board Setup (stackup, netclasses, constraints,
  `.kicad_dru`) is completed before placement. A DRC that passes against default rules proves
  nothing.
- **Every number is derived, never guessed.** Trace width, impedance, via count, thermal via
  array, creepage: run `scripts/pcb_calc.py` and show the inputs. If a value comes from a
  datasheet or fab capability sheet, name the source.
- **The fab's capability sheet is an input, not an afterthought.** Ask which fab and process
  class, or state the assumed profile explicitly (default: JLCPCB standard, 1 oz outer).
- **Never claim a board is DRC-clean without having run DRC**, or that files are correct
  without having opened the outputs. When KiCad is not installed in the environment, say so
  and hand the user the exact commands instead of implying they were run.
- **Prefer text-editable, diffable state.** Rules live in `<project>.kicad_dru`, exports in a
  jobset or script, everything in git. Never rely on a setting that exists only in someone's
  GUI session.
- Reference designators, net names, and sheet names are documentation. `NET_12` and `U7` with
  no value field is a board nobody can debug at 2 a.m.

## The gated workflow

Work gates in order. Each gate produces artifacts. Compress the gates for a two-resistor
breakout — never skip the thinking: state assumptions, failure modes, and how each is checked.

### Gate 0 — Product and manufacturing contract

Capture before drawing anything: function and interfaces; supply rails, currents, and worst-case
load; environment (temperature, humidity, shock, mains/SELV); enclosure and connector positions;
certification exposure (EMC, safety, radio); quantity and assembly route (hand, JLC/PCBA, local
CM); target fab and its capability class; cost and lead-time ceiling.

Deliverable: a filled [assets/templates/design-record.md](assets/templates/design-record.md).
Every later decision references a line in it. If the user is vague, choose sensible defaults,
**write them down as assumptions**, and proceed — do not stall the design on an interview.

### Gate 1 — Schematic architecture and capture

Block diagram and power tree with budgets → symbol/footprint decisions → hierarchical sheets →
ERC clean → BOM fields complete and sourced.

Read: [references/schematic-capture.md](references/schematic-capture.md),
[references/libraries-footprints.md](references/libraries-footprints.md).

### Gate 2 — Board setup

Layer count and stackup with real dielectric values, netclasses (with track/via/clearance/
diff-pair per class), board constraints set to the fab minimum, custom rules written, tuning
profiles for anything with a timing budget.

Read: [references/board-setup-stackup.md](references/board-setup-stackup.md),
[references/design-rules-dru.md](references/design-rules-dru.md). Start from a profile in
[assets/rules/](assets/rules/) rather than an empty rules box.

### Gate 3 — Placement

Mechanical-fixed parts → power converters → the loops that must stay small → sensitive analog/RF
→ everything else. Placement decides EMI, thermals, and routability; nothing here is cosmetic.

Read: [references/placement.md](references/placement.md).

### Gate 4 — Routing, planes, and tuning

Critical nets first, return paths verified layer by layer, planes poured last and inspected,
tuning applied to nets that have a timing constraint.

Read: [references/routing-planes.md](references/routing-planes.md),
[references/signal-integrity-rf.md](references/signal-integrity-rf.md),
[references/power-thermal.md](references/power-thermal.md).

### Gate 5 — Verification

ERC clean, DRC clean **with schematic parity**, every violation either fixed or excluded with a
written reason, plus the checks DRC cannot do: courtyard/3D collision, silkscreen legibility,
assembly access, thermal reality, review against the schematic intent.

Read: [references/review-checklists.md](references/review-checklists.md).

### Gate 6 — Release

Fab package generated by script or jobset, outputs re-imported and viewed before sending, fab
notes written, everything tagged in version control.

Read: [references/manufacturing-outputs.md](references/manufacturing-outputs.md).

## Non-negotiable design rules

- Every IC power pin gets its own decoupling capacitor at the pin, on the same side, with the
  via to the plane on the far side of the pad from the pin (loop area is the spec, not
  distance).
- No signal crosses a plane split or a plane void; every layer change on a fast net has a
  return via within a few mm.
- Switching converter hot loop (input cap → switch → diode/FET → back to cap) is the smallest
  physical loop on the board, on one layer, with a ground plane directly beneath.
- Crystals: shortest symmetric traces, ground guard, no copper and no routing under the can on
  any layer, load caps to a local quiet ground.
- Every connector that leaves the enclosure has ESD protection placed at the connector, with
  the return path to chassis/shield ground never crossing the logic ground.
- Copper widths are calculated for current and temperature rise; polygons for anything over
  ~500 mA. Show the calculation.
- Mains or >60 V: creepage and clearance per IPC-2221/IEC 60664 pollution degree, slots under
  optos/relays, no exceptions and no "it's only a prototype".
- Test points on every rail and every bring-up-critical signal; programming/debug pads on a
  grid that a pogo fixture can hit.
- Pin 1 markers, polarity marks, connector labels, board name and revision, and a date code
  field on silkscreen. Fiducials (3, asymmetric) if a machine places parts.
- DNP/exclude-from-BOM attributes set deliberately, not left at default.

## Reference files

Load the files the current gate needs; each is self-contained.

| Topic | File |
|---|---|
| Project structure, files, settings, version control | [references/project-setup.md](references/project-setup.md) |
| Schematic capture, hierarchy, ERC, BOM fields, variants | [references/schematic-capture.md](references/schematic-capture.md) |
| Symbols, footprints, padstacks, 3D models, KLC, part sourcing | [references/libraries-footprints.md](references/libraries-footprints.md) |
| Layer stack, materials, impedance targets, tuning profiles | [references/board-setup-stackup.md](references/board-setup-stackup.md) |
| Custom design rules language + rule cookbook | [references/design-rules-dru.md](references/design-rules-dru.md) |
| Placement methodology | [references/placement.md](references/placement.md) |
| Routing, vias, zones, teardrops, fills | [references/routing-planes.md](references/routing-planes.md) |
| Impedance, diff pairs, tuning, return paths, RF, EMC | [references/signal-integrity-rf.md](references/signal-integrity-rf.md) |
| PDN, copper sizing, thermal, high current, high voltage | [references/power-thermal.md](references/power-thermal.md) |
| Fab/assembly outputs, jobsets, panelization, fab notes | [references/manufacturing-outputs.md](references/manufacturing-outputs.md) |
| kicad-cli map, CI, kipy/IPC API, file formats, generating projects | [references/automation-scripting.md](references/automation-scripting.md) |
| Schematic/layout/pre-release review checklists | [references/review-checklists.md](references/review-checklists.md) |
| What changed in KiCad 9 and 10, and how to exploit it | [references/kicad-9-10-features.md](references/kicad-9-10-features.md) |

## Scripts

Run these instead of hand-computing or hand-assembling exports.

```bash
# Engineering math — every subcommand prints inputs, formula, and result
python3 scripts/pcb_calc.py trace-width --current 3 --rise 20 --layer external --copper-oz 1
python3 scripts/pcb_calc.py microstrip --er 4.4 --h 0.2104 --t 0.035 --z0 50      # solves width
python3 scripts/pcb_calc.py stripline --er 4.4 --h 0.5 --t 0.0152 --w 0.15
python3 scripts/pcb_calc.py diff-microstrip --er 4.4 --h 0.2104 --t 0.035 --w 0.34 --s 0.2
python3 scripts/pcb_calc.py prop-delay --er 4.4 --mode microstrip --length 50
python3 scripts/pcb_calc.py via-current --drill 0.3 --plating 0.025 --length 1.6 --current 2
python3 scripts/pcb_calc.py thermal-vias --power 1.5 --drill 0.3 --count 9 --thickness 1.6
python3 scripts/pcb_calc.py voltage-drop --current 2 --length 40 --width 1.0 --copper-oz 1
python3 scripts/pcb_calc.py creepage --voltage 230 --pollution 2 --material IIIa
python3 scripts/pcb_calc.py list                                                  # all subcommands

# Fabrication package: gates on ERC + DRC, then exports everything and zips it
bash scripts/fab_package.sh <project>.kicad_pro --profile jlcpcb --out fab/

# Static pre-fab audit of the design files (complements DRC, does not replace it)
python3 scripts/audit_project.py <project-dir> --profile jlcpcb
```

`pcb_calc.py` and `audit_project.py` are pure Python 3, no dependencies.
`fab_package.sh` requires `kicad-cli` on PATH.

## Working without KiCad installed

Claude often has no KiCad binary and no GUI. That does not prevent elite work — it changes the
deliverable. In that situation, produce: the design record, the block diagram and power tree
with budgets, the netlist-level schematic (part by part, pin by pin, with values derived), the
stackup and netclass table, a ready-to-paste `.kicad_dru`, a placement plan, a routing plan with
layer assignments and constraint per net, the calculations, the review checklist, and the exact
`kicad-cli` commands for the user to run. Say plainly which steps still need a KiCad session.
When files *can* be generated, see [references/automation-scripting.md](references/automation-scripting.md) §5
for the only reliable way to author KiCad files programmatically.
