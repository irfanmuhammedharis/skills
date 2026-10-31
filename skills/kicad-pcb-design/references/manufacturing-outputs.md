# Fabrication and Assembly Outputs

The design is not finished when DRC passes; it is finished when a stranger can build it from the
files without asking a question.

## Contents
1. What a complete release package contains
2. Gerber and drill export
3. Assembly data: BOM and position files
4. Modern alternatives: IPC-2581 and ODB++
5. Jobsets and one-command releases
6. JLCPCB / PCBWay specifics
7. Panelization
8. Fab notes and documentation
9. Verify before you send

---

## 1. What a Complete Release Package Contains

```
fab/rev-B/
  gerbers/            all copper, mask, silk, paste, Edge.Cuts, + drill files & map
  board-rev-B.zip     the archive the fab actually receives
  bom.csv             purchasing BOM (grouped, with MPN + supplier PN)
  cpl.csv             position/centroid file for assembly
  assembly.pdf        top/bottom assembly drawings with refdes
  schematic.pdf       full schematic
  fab-notes.md/pdf    stackup, finish, impedance, tenting, special processes
  board.step          3D model for mechanical
  ibom.html           interactive HTML BOM for hand assembly (optional but excellent)
  drc.json / erc.json evidence the release was clean
  README.md           what this is, which git tag, what changed since the last rev
```

## 2. Gerber and Drill Export

```bash
kicad-cli pcb export gerbers \
  --output fab/gerbers/ \
  --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --check-zones --no-protel-ext \
  board.kicad_pcb

kicad-cli pcb export drill \
  --output fab/gerbers/ --format excellon --drill-origin absolute \
  --excellon-units mm --excellon-separate-th --generate-map --map-format gerberx2 \
  board.kicad_pcb
```

- `--check-zones` refills zones before plotting — without it, a stale fill can ship.
- X2 attributes are on by default and help the fab; `--no-x2` only if their tooling chokes.
- `--subtract-soldermask` keeps silkscreen off exposed copper.
- `--excellon-separate-th` splits PTH and NPTH, which most fabs prefer; keep the map file so
  the drill table is human-readable.
- Add `Edge.Cuts` always; add `User.Comments`/`Dwgs.User` if your fab drawing lives there.
- For a variant build add `--variant <name>` (KiCad 10) and use `${VARIANT}` in output paths.

## 3. Assembly Data: BOM and Position Files

```bash
kicad-cli sch export bom \
  --output fab/bom.csv \
  --fields 'Reference,Value,Footprint,${QUANTITY},MPN,Manufacturer,LCSC,Datasheet' \
  --labels 'Designator,Value,Footprint,Qty,MPN,Manufacturer,LCSC Part #,Datasheet' \
  --group-by 'Value,Footprint,MPN' --sort-field Reference --exclude-dnp \
  schematic.kicad_sch

kicad-cli pcb export pos \
  --output fab/cpl.csv --format csv --units mm --side both \
  --use-drill-file-origin --exclude-dnp --smd-only \
  board.kicad_pcb
```

- Special fields available to `--fields`: `${QUANTITY}`, `${DNP}`, `${EXCLUDE_FROM_BOM}`,
  `${REFERENCE}`, `${VALUE}`, `${FOOTPRINT}`; `*` includes everything.
- Position data is only correct if footprint attributes (SMD/THT) and anchors are right —
  a footprint typed "unspecified" silently drops out of the CPL.
- `--use-drill-file-origin` keeps CPL coordinates consistent with the drill files; use the same
  origin for both, every revision.
- Rotation is the classic assembly failure: KiCad's zero-rotation convention is not every
  assembler's. Check a few parts (especially ICs, diodes, tantalums, and connectors) against the
  assembler's preview and correct with their rotation database or a corrected CPL.

## 4. Modern Alternatives: IPC-2581 and ODB++

```bash
kicad-cli pcb export ipc2581 --output fab/board.xml --units mm --compress \
  --bom-col-mfg-pn MPN --bom-col-mfg Manufacturer board.kicad_pcb
kicad-cli pcb export odb --output fab/board-odb.zip --compression zip --units mm board.kicad_pcb
```

Both carry netlist, stackup, and BOM data in one file, eliminating whole classes of gerber
ambiguity. If the fab accepts IPC-2581 or ODB++, send it *and* gerbers until you trust their
flow. `kicad-cli pcb export ipcd356` gives a netlist for bare-board electrical test — cheap
insurance on any board over a few hundred nets.

## 5. Jobsets and One-Command Releases

KiCad 9+ **jobsets** (`.kicad_jobset`) define the whole output set in the GUI and then run
headless:

```bash
kicad-cli jobset run --file release.kicad_jobset --stop-on-error project.kicad_pro
```

Use a jobset when the team works in the GUI; use `scripts/fab_package.sh` when the release must
run in CI with explicit gates. Either way the release is one command, reproducible from a git
tag, and never a sequence of manual dialogs.

## 6. JLCPCB / PCBWay Specifics

- Zip the gerbers + drill files at the *top level* of the archive (no nested folders).
- JLCPCB accepts KiCad's default gerber naming; verify the board outline is on `Edge.Cuts` and
  is a single closed contour.
- For JLCPCB assembly (PCBA): BOM needs `Comment/Value`, `Designator`, `Footprint`, and
  `LCSC Part #`; CPL needs `Designator, Mid X, Mid Y, Layer, Rotation`. Prefer **basic parts**
  where possible — extended parts add a per-part feeder fee.
- The **Fabrication Toolkit** plugin (bennymeg) exports gerbers + BOM + CPL in JLCPCB's expected
  format in one click and handles their rotation conventions; `JLC2KiCad_lib` / `easyeda2kicad`
  pull LCSC symbols/footprints/3D models into KiCad.
- Order options that must match the design: layer count, thickness, copper weight, surface finish
  (HASL vs ENIG — ENIG for fine pitch, BGA, or press-fit), mask/silk colour, via tenting, and
  impedance control with the named stackup. Declare each in the fab notes.
- Ordering across fabs: keep a per-fab profile in `assets/rules/` and switch the `.kicad_dru`
  when the fab changes; never assume the next fab's floor equals the last one's.

## 7. Panelization

- Ask the assembler what they want *before* designing the panel: rail width (usually 5–10 mm),
  fiducials (3 per panel, plus per-board for fine pitch), tooling holes, panel size limits,
  and whether they prefer V-cut, mouse bites, or routed tabs.
- V-cut requires straight edges and component keep-out from the scoring line (≥1 mm, more for
  tall parts); mouse bites leave a rough edge and need clearance from connectors/board edge
  components.
- **KiKit** panelizes from the CLI and is scriptable (`kikit panelize --preset :jlcpcb …`),
  which keeps the panel reproducible with the board rather than being a manual one-off.
- Panel first article: check the 3D/gerber view of the whole panel, not just one board.

## 8. Fab Notes and Documentation

Write [../assets/templates/fab-notes.md](../assets/templates/fab-notes.md) and send it with every
order. It states: board dimensions and thickness; layer count and named stackup; copper weights;
material and Tg; surface finish; mask and silk colours; minimum track/space and drill actually
used; impedance requirements with the controlled nets and target values; via treatment (tented,
plugged, filled/capped); slots, cutouts, castellations, edge plating; countersinks; panel
requirements; UL/date-code marking; IPC class (2 vs 3) and acceptance criteria; and who to
contact for a query.

The single most useful line in fab notes: *"if anything here is unclear or unmanufacturable,
contact us before proceeding — do not adjust the data."*

## 9. Verify Before You Send

- [ ] Re-import the generated gerbers into **GerbView** and look at every layer, including
      paste and mask, and the drill overlay. This catches inverted layers, missing pours, and
      silkscreen over pads faster than any checklist.
- [ ] Board outline: one closed loop, correct dimensions measured in the viewer.
- [ ] Drill table sane: no zero-diameter holes, no unexpected drill sizes, PTH/NPTH split correct.
- [ ] Copper layers correctly ordered top → bottom, with layer names matching the stackup.
- [ ] BOM: every line has MPN and supplier PN, quantities match the board, DNP handled, no
      "unspecified" values.
- [ ] CPL: refdes count matches the placed SMD count; spot-check three coordinates against the
      board; rotations checked against the assembler's convention.
- [ ] STEP export opens and matches the enclosure.
- [ ] ERC and DRC reports included in the package and clean (or with documented exclusions).
- [ ] Archive named with project, revision and date; git tag recorded in the README.
