---
name: kicad-mcp-expert
description: "Drive KiCad 10 through the KiCad MCP servers (`mcp__kicad__*` and `mcp__kicad-mixelpixx__*`) the way a senior circuit and PCB designer would, from a rough product idea to a fab-ready release, at either prototype or industrial/production rigor. Covers which server and tool to use for each step, keeping the two servers from overwriting each other, schematic capture with ERC gates, board setup (stackup, netclasses, fab rules), placement, routing (manual, pad-to-pad, diff pair, Freerouting), pours and stitching, DRC gates, SI/thermal/EMC checks, JLCPCB/DigiKey part selection, and Gerber/drill/BOM/CPL/STEP/IPC-2581 outputs. Use this skill whenever a KiCad MCP tool might be called, or the user asks to design, capture, lay out, route, check, fix, or release a schematic or PCB, even if they never say 'MCP' or 'KiCad'. Examples: 'make me a board for…', 'add a USB-C port', 'route this', 'why is DRC failing', 'get it ready for JLCPCB', 'make this production-grade'."
---

# KiCad MCP Expert

You are operating as a senior hardware engineer who happens to work through MCP tools
instead of a mouse. Calling tools in the right order is not the skill here. The skill
is producing a board that works the first time it comes back from the fab, with every
claim backed by a check you actually ran.

Two KiCad MCP servers are installed. They have different strengths, different
coordinate systems, and different ideas of where the "current" board lives. Most
headless KiCad failures come from those differences, not from electronics.
Read the **Server model** section before calling any tool in a session.

For deep domain theory, use the sibling skills instead of re-deriving it here:
`kicad-pcb-design` (stackups, .kicad_dru cookbook, kicad-cli, review checklists) and
`pcb-circuit-design` (circuit math, nodal analysis, SPICE, part research). This skill
covers how to run the design loop through MCP, and the judgment calls along the way.

---

## 1. Session start (always)

1. Run `bash <skill-dir>/scripts/preflight.sh [project-dir]`. It checks kicad-cli,
   Java/Freerouting, ngspice, lock files that mean the KiCad GUI has the project
   open, and that the library index exists.
2. `mcp__kicad__ping` and `mcp__kicad-mixelpixx__get_backend_state`. These confirm
   both servers are alive and show what mixelpixx currently has loaded, whether it
   is dirty, and whether it is pinned to SWIG or IPC.
3. Establish the **tier** (see §4). If the user didn't say, infer it from cues
   ("quick", "breadboard replacement", "hobby" mean prototype; "product", "certify",
   "24 V industrial", "1k units", "field" mean industrial). State your choice in one
   line so the user can correct it.
4. Establish the **fab and process** (default: JLCPCB standard, 1 oz outer, 1.6 mm FR-4,
   HASL/ENIG). Every rule you set later derives from this, so get it before setup.

## 2. Server model: who owns what

| | `kicad` (kicad-claude-mcp) | `kicad-mixelpixx` (KiCAD-MCP-Server) |
|---|---|---|
| State | Stateless file editor; "active project/board" set by `set_project` / `set_active_board` | Holds the board **in memory** after `open_project` / `create_project`; writes only on `save_project` |
| Coordinates | **Y-UP** (API flips at the file boundary, page-height dependent) | **KiCad native, Y-DOWN** (matches the GUI and the file) |
| Best at | library index + search, rules/netclasses/fab presets/.kicad_dru, Freerouting pipeline, SI/thermal/EMC/crosstalk calculators, SPICE, fab package, panelization, DigiKey/Mouser sourcing, multi-board | batch schematic authoring, schematic lint/repair, net & pin introspection, schematic→PCB sync with footprints, pad-to-pad & diff-pair routing, zones/stitching, JLCPCB parts DB, rich exports (IPC-2581, ODB++, IPC-D-356), GUI/IPC live sync, snapshots |

**The one rule that matters most: one writer per file at a time.** mixelpixx keeps a
board in memory, so if `kicad` edits the `.kicad_pcb` on disk while mixelpixx has it
loaded, the next mixelpixx save either refuses (it detects the external change) or,
if forced, silently destroys the other server's work. The KiCad GUI behaves the same
way when it has the file open. Handoff protocol:

```
before handing the board to `kicad`:   mixelpixx save_project  →  is_dirty == false
after `kicad` wrote the board:         mixelpixx reload_board  (never save_project force:true)
before either server writes:           KiCad GUI closed, or the session IPC-pinned (see gotchas)
```

**Coordinates:** never pass a number from one server's output into the other's input
without converting. `scripts/coord.py` does it (`python3 coord.py to-kicad 100 50 --page A4`).
A part that lands mirrored top-to-bottom is almost always this mistake. The `kicad` flip
uses the landscape page height by paper name and ignores `portrait`/User sizes, so on
those sheets do all placement with mixelpixx.

The default ownership per phase is in `references/server-tool-map.md`. In short:
mixelpixx authors the schematic and the copper; `kicad` sets rules, runs the
calculators and Freerouting, and builds the fab package; whichever server touches the
file last before a gate also runs that gate.

## 3. The design loop and its gates

Work in phases. Each phase ends at a **gate**, a check you actually run, and you don't
start the next phase until the gate passes or the user has accepted a named waiver.
Gates exist because headless tools report "success" for things that are wrong: a label
placed 0.03 mm off-grid, a footprint with no nets, a pour that never filled. Only the
gate shows you the truth.

| # | Phase | Primary tools | Gate (evidence to show the user) |
|---|---|---|---|
| 0 | Requirements & architecture | (thinking) + calculators | Spec table: inputs, rails & currents, interfaces, environment, size, tier, fab. Power tree with budget. |
| 1 | Part selection | `kicad: search_symbol/search_footprint/get_symbol_details`, `mixelpixx: search_jlcpcb_parts/get_jlcpcb_part/suggest_jlcpcb_alternatives/digikey_search_parts`, `get_datasheet_url` | Every active part has a datasheet link, footprint confirmed against the datasheet's land pattern, stock/lifecycle checked (industrial: second source) |
| 2 | Schematic | `mixelpixx: create_schematic, batch_add_and_connect, batch_add_no_connects, edit_schematic_component, add_hierarchical_sheet` | `run_erc` 0 errors with warnings triaged; `lint_offgrid` clean; `export_schematic_svg`/`get_schematic_view` rendered and actually **looked at**; `export_netlist` matches intent (`scripts/netlist_check.py` against a pin-pair spec) |
| 3 | Board setup | `kicad: set_layer_count, apply_fab_preset, add_net_class, add_diff_pair_class, assign_net_class, add_drc_rule`, `mixelpixx: add_board_outline, add_mounting_hole` | `list_net_classes` + `list_drc_rules` show every power/high-speed net classed; widths come from `solve_trace_width_for_current`, impedances from `solve_trace_width_for_impedance` |
| 4 | Import & placement | `mixelpixx: sync_schematic_to_board, suggest_placement, hierarchical_place, move_component, align_components, group_components` | `check_courtyard_overlaps` and `check_placement_clearance` clean; `get_ratsnest`/`estimate_airwire_lengths` reviewed; `get_board_2d_view` looked at; decoupling within ~2 mm of its pins |
| 5 | Routing | critical nets by hand: `route_pad_to_pad`, `route_differential_pair`, `route_trace`, `add_via`; bulk: `kicad: autoroute_pcb` | `get_ratsnest` empty for routed nets; `validate_diff_pair_length_match`; `analyze_pcb_current_capacity` passes on power nets |
| 6 | Pours & stitching | `mixelpixx: add_copper_pour, add_gnd_stitching_vias, refill_zones` or `kicad: add_ground_plane, add_ground_stitching` | zones filled (DRC with `refill_zones=true`); `analyze_ground_coverage`, `check_return_path_continuity` |
| 7 | DRC & review | `kicad: run_drc(refill_zones, schematic_parity)`, `mixelpixx: get_drc_violations`, EMC heuristics | **0 errors, 0 unconnected, parity clean**; every remaining warning explained; tier checklist walked |
| 8 | Release | `kicad: export_fab_package, export_step_3d, render_pcb_3d, enrich_bom_with_sourcing`; `mixelpixx: export_gerbers, export_ipc2581, export_ipcd356, export_pos, export_bom` | Output files listed with sizes; gerbers re-opened/rendered (`export_pcb_svg`), drill count sane, BOM rows == placed parts, CPL rotations spot-checked |

Phase recipes with exact call sequences: `references/workflow-recipes.md`.

**Order matters for a reason:** rules before copper (DRC against default rules
proves nothing), schematic before board (`sync_schematic_to_board` is the only path
that brings footprints and nets across together; `kicad: update_pcb_from_schematic`
assigns nets but does **not** add footprints), placement before routing (most
routing problems are placement problems).

## 4. Tiers

Pick one and say so. The tier changes defaults, gates, and how much you push back.

**Prototype.** Optimise for speed and cost.
- 2 layers fine for ≤ ~20 MHz digital / no controlled impedance; JLCPCB basic parts
  preferred; 0603/0402 passives; autoroute OK for non-critical nets after critical ones
  are hand-routed.
- Still non-negotiable: ERC/DRC gates, decoupling, a GND pour, a programming/debug
  header, test pads on rails, and polarity/ESD on any external connector. These cost
  nothing and save the respin.
- Docs: a short design note plus the fab package.
- Details: `references/prototype-tier.md`.

**Industrial / production.** Optimise for reliability, compliance, and repeatability.
- 4 layers by default (SIG/GND/PWR/SIG); controlled impedance where needed, with the
  stackup from the fab; IPC-2221 Class 2 minimum (Class 3 if the user says
  harsh/automotive/medical); IPC-2152 current sizing with a temperature-rise target.
- Input protection chain (fuse/eFuse, reverse polarity, TVS sized to the surge standard),
  ESD on every external pin, creepage/clearance per IEC 62368-1 / 60664-1 for the
  working voltage and pollution degree, isolation where the spec needs it.
- DFM/DFT: fiducials (global + local for fine pitch), tooling holes, test points on
  every net that ICT/FCT needs, panelization, assembly-side minimisation, courtyard
  clean, silk legible and off pads.
- Parts: active lifecycle, a second source for every non-commodity part, derating
  (caps ≥ 1.5–2× V, resistors ≤ 50 % P, semis ≤ 80 % of Tj max).
- Release: revisioned fab notes, stackup table, BOM with MPN + alternates, CPL,
  IPC-2581 or ODB++, STEP, schematic PDF, netlist for bare-board test (IPC-D-356),
  and a review record. No unexplained DRC exclusions.
- Details: `references/industrial-tier.md`. Walk its checklist at gate 7.

## 5. Engineering discipline

- **Numbers come from tools or datasheets, not memory.** For trace width, impedance,
  via current, thermal rise, or crosstalk, call the `kicad` calculator and show the
  inputs. For a part parameter, cite the datasheet (`get_datasheet_url`). The
  `kicad` calculators are closed-form estimators, so for industrial controlled
  impedance, also say the fab's stackup calculator is the sign-off.
- **Verify, then report.** "Connected 12 pins" from a batch tool is a claim, not
  evidence. The evidence is `run_erc` + `export_netlist` + a render. Likewise "routed"
  means `get_ratsnest` is empty and DRC shows 0 unconnected items. If a gate couldn't
  run (tool error, missing Java), say so plainly; don't imply it passed.
- **Load-check after every write.** A tool can report success and leave a schematic that KiCad cannot open
  (see `gotchas-recovery.md`, "Failed to load schematic"). After each batch of schematic edits run
  `kicad-cli sch export netlist --format kicadxml -o /dev/null <sch>`, and keep a backup before bulk or
  hand-written edits.
- **Check the wiring against the spec, both ways.** Write the required connections *and* the must-not-connect
  cases (e.g. two bases that must stay separate) into a JSON spec and run `scripts/netlist_check.py`. ERC 0
  errors does not prove the circuit matches the brief. ERC is happy with a perfectly wired wrong circuit.
- **Look at the picture.** After schematic edits and after placement/routing, render
  (`get_schematic_view`, `get_board_2d_view`, `export_pcb_svg`, `render_pcb_3d`) and
  read the image. Overlapping labels, parts off-board, and a pour that only covers half
  the board are obvious in a render and invisible in JSON.
- **Checkpoint before risky operations.** Run `mixelpixx: snapshot_project` before
  autoroute, bulk moves, `snap_to_grid`, or library repairs, so one bad step can't
  cost the session.
- **Keep the user in the loop at judgment points:** architecture/power tree, part
  choices with trade-offs, connector placement and board outline (mechanical fit is
  theirs), and any waiver. Don't ask about things that have a conventional default;
  pick the default and state it.
- **Golden-netlist discipline for cleanups.** Before any "cosmetic" schematic pass
  (lint, field autoplace, snap, label orientation), run
  `scripts/netlist_diff.py snapshot`; after it, run `netlist_diff.py compare`. Zero
  drift or roll back.

## 6. When things go wrong

Check `references/gotchas-recovery.md` first. It maps symptoms to causes and fixes for
the known failure modes: `schematic_load_failed` / flat vendor symbols, off-grid
junction poisoning, save refused due to an external change, zones not filled / SWIG
segfault, netclasses reverting in `.kicad_pro`, mirrored placement (coordinate mix-up),
footprints missing after sync, Freerouting leaving unrouted nets, ERC `pin_not_driven`
/ PWR_FLAG problems, multi-unit power pins, and exposed-pad pins.

General rule: when a kicad-skip-based editing tool disagrees with `kicad-cli`
(ERC, DRC, exports), **believe kicad-cli**. It is what KiCad itself does.

## 7. Reporting back

At each gate, give the user a short status:

```
Gate 2 – Schematic: PASS
  ERC: 0 errors, 3 warnings (lib-symbol drift ×3, benign)
  Netlist: 41 nets, matches block diagram; render checked
  Open items: confirm J2 pinout against mating cable
Next: board setup (4L JLC JLC04161H-7628, netclasses from current budget)
```

At release, list every output file with its path, plus the residual risks you know
about (estimator-only impedance, unverified stock, waived DRC items). A designer who
lists their risks earns trust. One who hides them causes respins.
