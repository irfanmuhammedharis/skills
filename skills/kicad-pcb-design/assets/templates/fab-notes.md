# Fabrication Notes — <project> rev <X>

Send with every order. If anything below is unclear or unmanufacturable, contact us
before proceeding — **do not adjust the data**.

Contact: <name, email, phone>   Date: <YYYY-MM-DD>   Git tag: <tag>

## Board

| Item | Value |
|---|---|
| Dimensions | … × … mm (see Edge.Cuts; single closed outline) |
| Thickness | 1.6 mm ±10% |
| Layer count | 4 |
| Named stackup | JLC04161H-7628 (or: see stackup drawing) |
| Base material / Tg | FR-4, Tg ≥150 °C |
| Outer copper | 1 oz (35 µm) finished |
| Inner copper | 0.5 oz |
| Surface finish | ENIG (or HASL lead-free) |
| Solder mask | green, both sides |
| Silkscreen | white, both sides |
| Minimum track / space used | 0.20 mm / 0.20 mm |
| Minimum drill used | 0.30 mm |
| Via treatment | tented both sides, except test vias listed below |
| Edge plating / castellations | none |
| Slots / cutouts | on Edge.Cuts, see drawing |
| Countersinks / chamfers | none |
| Panelization | single boards / panel per assembler spec below |
| IPC class | 2 (or 3 — state acceptance criteria) |
| Date code / UL marking | in copper on B.Cu at … / not required |
| RoHS | required |

## Controlled impedance

Required: yes / no

| Net group | Layer | Structure | Target | Tolerance | Width / gap as drawn |
|---|---|---|---|---|---|
| USB_D± | L1 | differential microstrip over L2 GND | 90 Ω | ±10% | 0.30 / 0.20 mm |
| RF | L1 | CPWG over L2 GND | 50 Ω | ±10% | 0.37 / 0.20 mm |

Adjust trace widths to hit the impedance target **only after contacting us**.

## Assembly (if applicable)

| Item | Value |
|---|---|
| Sides populated | top only / both |
| Process | reflow (SAC305, lead-free) |
| Stencil | 0.12 mm, thermal pads windowpaned per paste layer |
| Fine pitch parts | U1 QFN-48 0.5 mm pitch |
| Moisture sensitive parts | per manufacturer MSL |
| DNP components | per BOM; do not substitute |
| Substitutions | not permitted without written approval |
| Fiducials | 3 global, plus local fiducials at U1 |
| Panel rails / tooling | rails 5 mm both long edges, 3 fiducials per panel |
| Depanel method | V-cut / mouse bites |
| First article | photos of top and bottom before full run |

## Files supplied

| File | Contents |
|---|---|
| `<project>-<rev>-gerbers.zip` | Gerber X2 + Excellon drill (PTH/NPTH separate) + drill map |
| `bom.csv` | BOM, DNP excluded, MPN and supplier part numbers |
| `cpl.csv` | placement, mm, drill-file origin, SMD only |
| `<project>-assembly.pdf` | assembly drawing, top and bottom |
| `<project>-netlist.d356` | IPC-D-356 netlist for bare-board electrical test |
| `<project>.step` | 3D model for reference |

Electrical test: required on all boards (netlist supplied).

## Known deviations

Anything intentionally outside the standard process, with the reason:

- …
