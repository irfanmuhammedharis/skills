# Design Record — <project> rev <X>

One document per board revision. Every decision that a reviewer or future-you would
otherwise have to reverse-engineer lives here. Keep it in the repo beside the project.

## 1. Purpose and requirements

| ID | Requirement | Source | How it is met | Verified by |
|---|---|---|---|---|
| REQ-FUN-001 | | | | |
| REQ-PWR-001 | | | | |
| REQ-ENV-001 | | | | |
| REQ-MEC-001 | | | | |
| REQ-EMC-001 | | | | |

Assumptions made in the absence of a stated requirement (each one is a question the
customer never answered — flag them for confirmation):

- …

## 2. Interfaces and connectors

| Connector | Function | Mating part | Pinout ref | Protection | Notes |
|---|---|---|---|---|---|

## 3. Power tree

| Rail | Source | Converter | V (tol) | I max (worst case) | Headroom | Sequencing | Loads |
|---|---|---|---|---|---|---|---|

Total input power: … Efficiency assumption: … Thermal consequence: …

## 4. Calculations

Paste the `pcb_calc.py` output for each. Every width, via count, and capacitance in the
design traces back to a line here.

| What | Inputs | Result | Where used |
|---|---|---|---|
| Trace width, 3 V3 rail | 2 A, 20 °C rise, 1 oz external | 0.60 mm → used 1.0 mm | Power netclass |
| … | | | |

## 5. Stackup and impedance

- Fab and process class: …
- Layer count and named stackup: …
- Layer assignment: L1 …, L2 …, L3 …, L4 …
- Controlled impedance nets and targets: …
- Calculated geometries (width/gap per target): …

## 6. Netclasses and design rules

| Class | Nets | Track | Clearance | Via | Why |
|---|---|---|---|---|---|

Custom rules added and what each protects: …

## 7. Component decisions

| Part | Choice | Alternatives considered | Why | Availability / second source |
|---|---|---|---|---|

## 8. Placement and layout decisions

Constraints that drove the layout (mechanical, thermal, EMI), what was traded away, and
anything a future revision should revisit.

## 9. Verification evidence

| Check | Command / method | Result | Date |
|---|---|---|---|
| ERC | `kicad-cli sch erc …` | | |
| DRC + parity | `kicad-cli pcb drc --schematic-parity …` | | |
| Static audit | `python3 audit_project.py …` | | |
| 3D / enclosure fit | | | |
| Gerber visual review | GerbView, layer by layer | | |

DRC exclusions and the reason each is acceptable:

| Violation | Location | Why accepted |
|---|---|---|

## 10. Bring-up plan and measured results

Expected values before power-on, and what was actually measured. This is what makes
revision B a data-driven design rather than a second guess.

| Measurement | Expected | Measured | Notes |
|---|---|---|---|
| Input current at idle | | | |
| Each rail voltage / ripple | | | |
| Thermal rise, hottest part | | | |

## 11. Change log

| Rev | Date | Change | Reason |
|---|---|---|---|
