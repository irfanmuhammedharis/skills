# Project Setup and File Hygiene

What lives where, what to commit, and the settings that must be right before any design work.

## Contents
1. Project files and what each controls
2. Repository layout
3. Library table strategy
4. Project settings that matter
5. Version control and review
6. Multi-board and reuse

---

## 1. Project Files and What Each Controls

| File | Format | Role | Commit? |
|---|---|---|---|
| `x.kicad_pro` | JSON | Project settings: netclasses, DRC constraints, severities, text vars, BOM/plot presets, tuning profiles | Yes |
| `x.kicad_sch` | S-expr | Root schematic; each hierarchical sheet is its own `.kicad_sch` | Yes |
| `x.kicad_pcb` | S-expr | Board: stackup, footprints, tracks, zones, plot params | Yes |
| `x.kicad_dru` | S-expr | Custom design rules (text, one file per project) | Yes |
| `x.kicad_prl` | JSON | Local UI state (visible layers, zoom, last used values) | No |
| `x.kicad_jobset` | JSON | Named output jobs (KiCad 9+), runnable via `kicad-cli jobset run` | Yes |
| `fp-lib-table` / `sym-lib-table` | S-expr | Library tables (global in config dir, project-local in project dir) | Project ones: yes |
| `x-backups/` | zip | Auto backups | No |
| `*.kicad_sym` / `*.pretty/*.kicad_mod` | S-expr | Project symbol/footprint libraries | Yes |

`fp-info-cache`, `*.net`, `*.step`, gerbers and other generated artifacts are build output —
regenerate them, don't commit them (except a tagged release folder if the shop wants it).

## 2. Repository Layout

```
project/
  hardware/
    project.kicad_pro / .kicad_sch / .kicad_pcb / .kicad_dru / .kicad_jobset
    sheets/            # hierarchical sub-sheets
    lib/
      project.kicad_sym
      project.pretty/          # project-specific footprints
      3d/                      # STEP models referenced with ${KIPRJMOD}
    fp-lib-table  sym-lib-table # project-scoped, using ${KIPRJMOD} paths
  docs/  design-record.md, fab-notes.md, review checklists, datasheets/
  fab/   generated per revision, e.g. fab/rev-B/ (tagged, not tracked day to day)
  firmware/
```

Always reference project libraries and 3D models through `${KIPRJMOD}` so the project builds on
any machine. Absolute paths are the single most common reason a colleague opens a board full of
missing footprints.

## 3. Library Table Strategy

- Official KiCad libraries: use as-is for passives, connectors, and generic parts. They are
  well-generated (v10 ships STEP-only 3D models, ~78% of footprints machine-generated).
- Project library (`project.kicad_sym` + `project.pretty`): anything custom, anything modified,
  anything whose footprint you verified against a specific datasheet drawing.
- Never edit an official library in place — copy the symbol/footprint into the project library,
  rename it, and edit there. Official libs update and will overwrite you.
- A part is "in the library" only when symbol + footprint + 3D model + MPN + supplier part
  number all exist and the footprint has been checked against the datasheet's recommended land
  pattern. Half a part is worse than no part.

## 4. Project Settings That Matter

Set these in **Board Setup** before layout (details in board-setup-stackup.md and
design-rules-dru.md):

- **Physical stackup**: real layer thicknesses and dielectric constants from the fab, not
  defaults. Everything impedance-related and the 3D/STEP export depend on it.
- **Constraints**: absolute board minima = fab minima. A minimum here cannot be relaxed by a
  netclass or custom rule later, so set it to the process floor and use netclasses for anything
  more generous.
- **Netclasses**: Default, Power, GND, and one per constrained signal group (USB, RF50,
  DIFF90, HV). Assign by net name pattern in the netclass panel so new nets inherit correctly.
- **Pre-defined track/via sizes**: the two or three widths you actually intend to use, so
  routing snaps to intent instead of drifting.
- **Violation severities**: promote to error anything you refuse to ship with (e.g. silk over
  pads, courtyard overlap). Downgrading a severity is a design decision — record why.
- **Text variables** (`${VAR}`): board revision, date, project name, so title blocks and
  silkscreen strings are edited in one place and appear in exports.

In **Schematic Setup**: ERC severities, symbol field name templates (MPN, Manufacturer, LCSC,
Datasheet, Tolerance, Voltage), and the BOM preset used at release.

## 5. Version Control and Review

- Git works well: KiCad files are text S-expressions. Set a `.gitattributes` marking
  `*.kicad_pcb` and `*.kicad_sch` as text; add `*.kicad_prl`, `*-backups/`, `fp-info-cache`,
  `*.net`, `fab/` to `.gitignore`.
- Diffs of raw S-expressions are unreadable for layout. For real review use
  `kicad-cli sch export pdf` / `pcb export pdf` per revision and diff the PDFs or images, or
  KiCad's built-in Git integration and board-diff tooling. `kicad-cli gerber diff` (KiCad 11+)
  compares fabrication output directly — the strongest regression check for a respin.
- Commit at meaningful states: "schematic ERC clean", "placement frozen", "routing complete,
  DRC clean", "rev B released". Tag releases; the tag is what the fab package is built from.
- CI: run ERC and DRC on every push (see automation-scripting.md §4). A board that only passes
  DRC on the designer's laptop is not verified.

## 6. Multi-Board and Reuse

- **Design blocks** (schematic, and PCB in KiCad 10): save a proven sub-circuit *with its
  layout* — buck converter, USB-C front end, ESP32 module block — and reuse it across projects.
  This is the highest-leverage habit in KiCad 10; a converter you laid out once and measured is
  worth more than any generic app-note copy.
- **Multichannel / replicate layout**: for N identical channels, lay out one, replicate the rest;
  keeps them consistent and makes review tractable.
- **Variants** (KiCad 10): one schematic and board, multiple BOM/fit configurations. Use for
  regional options, populated/unpopulated features, and dev vs production builds. Exports take
  `--variant <name>`, so each variant gets its own BOM/CPL from the same source of truth.
- Inter-board connections (mezzanine, ribbon): document the pin mapping in the design record and
  keep both boards' connector symbols pin-for-pin consistent; mirrored connectors are a classic
  respin cause.
