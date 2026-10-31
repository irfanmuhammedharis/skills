# Automation, CLI, and Scripting

## Contents
1. Versions and what changed
2. `kicad-cli` command map
3. Verification commands (the ones that gate a release)
4. CI pipelines
5. Generating and editing KiCad files programmatically
6. The IPC API (kipy) and plugins
7. Useful external tools

---

## 1. Versions and What Changed

- **KiCad 10** (stable since March 2026, 10.0.x) is the assumption in this skill.
  `kicad-cli` subcommands: `fp`, `jobset`, `pcb`, `sch`, `sym`, `version`.
- **KiCad 9** is broadly compatible; it lacks variants, time-domain tuning, the graphical DRC
  rule editor, PCB design blocks, and `--variant` on exports.
- Nightly/KiCad 11 adds `kicad-cli api-server` (headless IPC) and a `gerber` subcommand
  (`convert png`, `diff`, `info`) — very useful for regression-diffing fabrication output.
- The **SWIG `pcbnew` Python module still exists in 9 and 10 but is removed in KiCad 11.**
  Do not write new automation against it. Use `kicad-cli`, the IPC API (`kicad-python`/kipy), or
  direct file manipulation instead.
- Check with `kicad-cli version` and `kicad-cli version --format about` (the latter is what to
  paste into bug reports). On macOS the binary lives at
  `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.

## 2. `kicad-cli` Command Map

```
kicad-cli sch  erc | export {bom, python-bom, netlist, pdf, svg, dxf, ps, png} | upgrade
kicad-cli pcb  drc | render | import | upgrade
               export {gerbers, drill, pos, pdf, svg, png, dxf, ps,
                       step, stepz, glb, brep, ply, stl, u3d, 3dpdf,
                       ipc2581, ipcd356, odb, gencad, statistics}
kicad-cli fp   export svg | upgrade          # .pretty libraries, Altium/EAGLE/EasyEDA import
kicad-cli sym  export svg | upgrade
kicad-cli jobset run --file x.kicad_jobset project.kicad_pro
```

Flags that repay knowing:

- `-D KEY=VALUE` / `--define-var` — override project text variables at export time (revision,
  build ID, variant labels) without editing the board.
- `--variant NAME` — per-variant outputs (KiCad 10); `${VARIANT}` expands in output paths.
- `--check-zones` (plot commands) — refill zones before plotting.
- `--drawing-sheet` — swap the title block for a customer-specific one.
- `--exclude-dnp`, `--hide-DNP-footprints-on-fab-layers`, `--crossout-DNP-footprints-on-fab-layers`
  — DNP handling in assembly documentation.
- `--theme`, `--black-and-white` — readable PDFs for review and print.

## 3. Verification Commands (The Ones That Gate a Release)

```bash
kicad-cli sch erc --severity-error --exit-code-violations \
    --format json -o build/erc.json project.kicad_sch

kicad-cli pcb drc --schematic-parity --severity-error --exit-code-violations \
    --refill-zones --format json -o build/drc.json project.kicad_pcb
```

- Exit code **5** means violations were found (0 = clean); that is what a CI job checks.
- `--schematic-parity` is not optional: it catches nets and footprints that drifted between
  schematic and board.
- `--severity-all` when you want warnings and exclusions in the report too;
  `--severity-exclusions` alone shows what has been silenced — review it every release.
- `--all-track-errors` reports every violation per track rather than the first.
- JSON output is machine-readable: count violations by type, fail the build on regressions,
  and attach the file to the release.

## 4. CI Pipelines

A minimal, high-value pipeline (GitHub Actions, GitLab CI, or a local pre-tag script) using a
container with KiCad installed:

```yaml
steps:
  - run: kicad-cli version
  - run: kicad-cli sch erc --severity-error --exit-code-violations -o erc.rpt hw/project.kicad_sch
  - run: kicad-cli pcb drc --schematic-parity --severity-error --exit-code-violations
                          --refill-zones -o drc.rpt hw/project.kicad_pcb
  - run: bash scripts/fab_package.sh hw/project.kicad_pro --out artifacts/
  - run: python3 scripts/audit_project.py hw --profile jlcpcb
  - uses: upload-artifact  # gerbers, BOM, CPL, PDFs, DRC/ERC reports
```

Add on tags: build the fab package, attach it to the release, and keep the STEP and PDFs so a
future revision can be diffed against this one.

## 5. Generating and Editing KiCad Files Programmatically

KiCad files are S-expressions (`.kicad_sch`, `.kicad_pcb`, `.kicad_sym`, `.kicad_mod`,
`.kicad_dru`) plus JSON (`.kicad_pro`, `.kicad_jobset`). Millimetres, Y axis pointing down,
UUIDs on most objects.

Order of preference:

1. **Let KiCad write KiCad files.** Author in the GUI, or start from a template project and edit
   only the parts you understand. Generated files that KiCad has never saved often lack default
   sections other tools expect.
2. **`.kicad_dru`, `.kicad_pro`, `.kicad_jobset`, netclass definitions, BOM presets** are safe
   and valuable to generate or template — they are simple, stable, and text-first.
3. **Schematic generation from a netlist description**: use `kicad-skip` (read/modify existing
   `.kicad_sch`), or a hardware-description approach (SKiDL, atopile) that emits a netlist which
   KiCad imports into a board. Generating a *readable* schematic from scratch is genuinely hard;
   generating a correct netlist is not.
4. **Hand-writing S-expressions**: acceptable for small footprints and simple boards. Two rules:
   never invent a `(version …)` token — copy one from a file the installed KiCad wrote — and
   normalise the result with `kicad-cli pcb upgrade` / `sch upgrade`, then open it in ERC/DRC to
   prove it parses. `--force` re-saves even if already current.
5. Round-trip safety: KiCad rewrites files on save with its own formatting, so keep generated
   content in *separate* files (a sub-sheet, a project library, the `.kicad_dru`) rather than
   interleaving it with human edits in one file.

When Claude has no KiCad binary, everything in tier 2 and the netlist in tier 3 can still be
produced and handed over with confidence; do not claim a hand-written `.kicad_pcb` opens
correctly without having opened it.

## 6. The IPC API (kipy) and Plugins

```bash
pip install kicad-python     # module name: kipy
```

```python
from kipy import KiCad
kicad = KiCad()                      # connects to a running KiCad session
board = kicad.get_board()
for fp in board.get_footprints():
    print(fp.reference_field.text.value, fp.position, fp.layer)
commit = board.begin_commit()
# ... modify items ...
board.update_items(changed)
board.push_commit(commit)            # one undo step for the user
```

- Requires KiCad running with **Preferences → Plugins/Scripting → Enable IPC API** (protobuf over
  a local socket). Unlike the old SWIG bindings, there is no headless-in-process mode in 9/10 —
  use `kicad-cli` for batch work and kipy for interactive/session automation.
- KiCad 9 exposed the PCB editor only; KiCad 10 extends the API further (schematic access), and
  export/plot APIs arrive in KiCad 11 — until then, call `kicad-cli` from a plugin for exports.
- Wrap edits in a commit so the user gets a single undo, and never mutate a board the user is
  mid-edit on without telling them.
- Plugins are installed through the **Plugin and Content Manager**; an IPC plugin is a directory
  with a manifest plus your script, which makes distribution to a team trivial.

## 7. Useful External Tools

| Tool | Use |
|---|---|
| **KiKit** | Panelization, manufacturing data export, presets per fab; scriptable and CI-friendly |
| **InteractiveHtmlBom** | Clickable BOM/placement page — the fastest way to hand-assemble a board |
| **Fabrication Toolkit** (bennymeg) | One-click JLCPCB gerbers + BOM + CPL with correct conventions |
| **JLC2KiCad_lib / easyeda2kicad** | Generate KiCad symbol + footprint + 3D model from an LCSC part number |
| **kicad-skip** | Pythonic read/modify of `.kicad_sch` files |
| **SKiDL / atopile** | Describe circuits in code, emit netlists |
| **freerouting** | External autorouter via DSN/SES — for low-consequence nets only, always reviewed |
| **KiCost / KiBoM** | Costed and configurable BOMs |

Treat every third-party output as untrusted input: verify footprints against the datasheet and
re-run DRC after any tool touches the board.
