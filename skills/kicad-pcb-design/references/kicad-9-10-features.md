# KiCad 9 and 10: What Changed and How to Exploit It

Knowing the current feature set is what separates advice that sounds right from advice that is
current. KiCad 10.0.0 was released 2026-03-20; bug-fix releases follow roughly monthly
(10.0.6 as of late August 2026). KiCad 9.0.x remains in maintenance.

## KiCad 10 highlights that change how you work

**Design variants** — one schematic and board, multiple fit/BOM configurations, with per-variant
field values. Every relevant export takes `--variant NAME`, and `${VARIANT}` expands in output
paths. Replaces parallel projects for regional or optioned builds. Documentation is still thin,
so record your variant conventions in the design record.

**Time-domain tuning and tuning profiles** — a rebuilt tuning system where profiles define
per-layer propagation parameters (impedance, delay, reference plane) and attach to netclasses.
The router and DRC then agree, tuning can target picoseconds instead of millimetres, and
pad-to-die delay is a first-class pad field. Use it for anything routed across layers with a
timing budget; stay in length mode when the spec is written in length.

**Graphical DRC rule editor** — build custom rules through a dialog; the output is the same
custom-rules language, so GUI-created rules stay text-editable and diffable. Good entry point for
a team; the text file is still the source of truth.

**Jumpers** — declare pins/pads that are internally or externally connected (solder bridges,
links, off-board connections). They share a net and produce no ratsnest, which is the honest way
to model shorting links instead of inventing nets.

**PCB design blocks** — reusable *layout* blocks, extending the KiCad 9 schematic design blocks.
Lay out a proven converter or USB front end once, reuse it with its routing. The highest-leverage
feature in the release for anyone who builds similar products repeatedly.

**Pin and gate swap** with forward and back annotation — unconstrained swapping in the PCB,
pushed back into the schematic, so routability fixes do not desynchronise the design.

**Inner-layer objects in footprints** — graphics, keepouts, and shapes on inner layers inside a
footprint, which finally makes correct RF and BGA footprint definitions possible.

**New importers**: Allegro, PADS, and gEDA/Lepton, on top of the existing Altium, EAGLE, CADSTAR,
EasyEDA/JLCEDA support (`kicad-cli fp upgrade` handles library conversion).

**Also**: 3D PDF export, barcodes as native objects, hatched fills in graphic shapes, native
rounded rectangles, precise polygon point editing, suggested fix actions for DRC errors, hop-over
wire crossings, schematic grouping, local power symbols, pin-table CSV import/export, lasso
selection, customisable toolbars, undo inside dialogs, and Windows dark mode.

**Libraries**: STEP-only 3D models (smaller install, better geometry), ~78% of footprints now
generated from data, plus ~950 new symbols and ~1200 new footprints since KiCad 9.

## KiCad 9 features still worth knowing

Multiple netclasses per net (hence `hasNetclass()` in rules), the `creepage` DRC constraint,
schematic design blocks, jobsets (`.kicad_jobset` + `kicad-cli jobset run`), the IPC API and
IPC plugin system, ODB++ and IPC-2581 export, and embedded files in projects.

## Version-sensitive gotchas

- `kicad-cli api-server` (headless IPC) and the `gerber` subcommand are nightly/KiCad 11, not 10.0.
- The SWIG `pcbnew` Python module exists in 9 and 10 but is **removed in KiCad 11** — port
  automation to kipy or `kicad-cli` now.
- IPC API export/plot functions land in KiCad 11; in 9/10 call `kicad-cli` from plugins.
- Time-domain parameters entered in a 10.0 release candidate did not carry into 10.0.0 final.
- Opening a KiCad 9 project in 10 upgrades the files; the reverse does not work. Branch or tag
  before upgrading a project that others still open in 9.
- File format `(version …)` tokens change between releases — never invent one; copy from a file
  the installed KiCad wrote, or run `kicad-cli pcb upgrade` / `sch upgrade`.

## Staying current

Feature sets move once a year and bug-fix releases monthly. Before asserting that KiCad cannot do
something, check the current release notes at kicad.org/blog and the reference manual at
docs.kicad.org for the installed major version — and `kicad-cli <subcommand> -h`, which is always
the truth for the binary in front of you.
