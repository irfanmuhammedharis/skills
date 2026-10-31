# Workflow recipes

Concrete call sequences per phase. Parameters are illustrative. Check the loaded tool
schema for exact names. K = `mcp__kicad__`, M = `mcp__kicad-mixelpixx__`.

## Contents
- R0 Requirements capture template
- R1 New project bootstrap
- R2 Building one schematic block
- R3 Power tree & rails (with PWR_FLAG logic)
- R4 Board setup from the fab profile
- R5 Import + placement
- R6 Routing order
- R7 Autoroute handoff
- R8 Pours, stitching, fill
- R9 DRC triage loop
- R10 Release package
- R11 Editing an existing design (ECO)

---

## R0. Requirements capture
Before touching a tool, fill this in (ask only for what you can't infer):

| Item | Value |
|---|---|
| Function (one sentence) | |
| Input power (range, source, connector, transients) | |
| Rails (V, I max, noise tolerance) | |
| Interfaces (USB/CAN/RS-485/Ethernet/RF/sensors/debug) | |
| MCU / main IC (or "pick for me") | |
| Environment (temp range, humidity, vibration, enclosure IP) | |
| Size / mounting / connector positions | |
| Tier (prototype / industrial) + volume | |
| Fab + assembly (JLCPCB/PCBWay/local; who assembles) | |
| Compliance targets (CE/FCC/UL/IEC 61000-4-x, 62368, automotive) | |

Then write the power tree with a budget (`rail ← source, Iload, Pdiss, efficiency`)
and use K `simulate_thermal_steady_state` for any linear regulator dissipating > ~0.5 W.

## R1. New project bootstrap
```
bash scripts/preflight.sh <dir>                       # environment + GUI lock check
M create_project(path=<dir>, name=<name>)
K set_project(project_path=<dir>)
K index_libraries                                    # first time on this machine only
M get_backend_state                                  # expect swig-pinned, clean
```
Prefer one sheet per functional block for anything over ~25 parts. Make the root sheet a
block diagram of hierarchical sheets.

## R2. Building one schematic block
```
M batch_list_symbol_pins([...symbols])               # learn real pin numbers/names first
M batch_add_and_connect(schematicPath, labelType: "label"|"global_label",
    components: [{symbol, reference, value, footprint, position{x,y}, nets{pin:NET}}])
M batch_add_no_connects(schematicPath, pins: [...])  # only truly unused pins
M edit_schematic_component(... properties: {MPN, Manufacturer, LCSC, Datasheet})
M lint_offgrid(schematicPath)                        # fix:true if anything is reported
M run_erc(schematicPath)
M get_schematic_view(...)                            # read the picture
M export_netlist / list_schematic_nets               # confirm NET→REF.PIN map
```
Layout conventions an experienced reviewer expects: signal flow left→right, power at
the top and GND at the bottom, decoupling caps drawn next to the pin they serve and
named by that pin, every connector pin labelled with its net, and test points drawn
as symbols (`TestPoint:TestPoint`) so they reach the BOM and CPL.

Assign the footprint **at placement**. A symbol without a footprint arrives on the board
as nothing.

## R3. Power tree & PWR_FLAG
- A rail driven by a regulator pin typed `power_output` needs no flag.
- A rail fed only by a connector/passive (e.g. VBUS from USB-C, +24V from a terminal
  block) needs exactly **one** `power:PWR_FLAG`, on the sheet where the rail
  originates.
- Two drivers on one net show up as `Power output and Power output are connected`.
  Remove the extra flag.
- Vendor regulator symbols often type outputs `passive`, so they need a flag. Check
  with `list_symbol_pins`.
- Exposed pads (QFN/DFN EP) are often `power_input`. Tie them to GND explicitly.
- Multi-unit ICs with a separate power unit (74xx, op-amp quads): place the power unit.

## R4. Board setup from the fab profile
```
K set_layer_count(n=2|4|6)                           # before any inner-layer copper
K list_fab_presets → K apply_fab_preset(<preset>)
K solve_trace_width_for_current(I, ΔT=10, copper_oz) # per power rail
K solve_trace_width_for_impedance(Z0=90 diff / 50 SE, stackup) # if any controlled nets
K add_net_class("Power", track_width_mm, clearance_mm, via...)
K add_diff_pair_class("USB", diff_pair_width_mm, diff_pair_gap_mm)
K assign_net_class(net_pattern="+5V|VBUS|+3V3", class_name="Power") ...
K add_drc_rule(...)                                  # creepage, HV, length, keep-outs
M add_board_outline(shape, w, h, cornerRadius)       # Y-down coords
M add_mounting_hole × n                              # M3: 3.2 mm drill, keep-out ring
M reload_board                                        # pick up K's .kicad_pro/.kicad_dru edits
```
Typical starting widths (always re-derive): signals 0.15–0.25 mm, 1 A ≈ 0.4–0.5 mm on
1 oz outer at ΔT 10 °C, 3 A ≈ 1.5–2 mm or a pour.

## R5. Import + placement
```
M save_project (schematic final) → M sync_schematic_to_board(schematicPath, boardPath)
M save_project → K update_pcb_from_schematic        # renames nets to the schematic's names; do this BEFORE routing
M reload_board
M get_component_list                                 # every ref present, none at (0,0) stacked
M suggest_placement / hierarchical_place             # optional starting spread
```
Then place in this order, because each step constrains the next:
1. **Mechanical & connectors** at their required edges/positions (user-confirmed).
2. **Main IC(s)** oriented so their pin groups face what they connect to.
3. **Power stages.** Keep the switching loop (input cap, switch, diode/low-side FET) as
   small as possible, inductor close, and FB divider near the FB pin and away from the SW node.
4. **Decoupling.** Smallest value closest to the pin, via to GND right at the cap pad.
5. **Crystals** within a few mm of the MCU with a guard ring of GND, no traces underneath.
6. **ESD/TVS** right at the connector, before anything else on the net.
7. **RF** at the board edge with the antenna keep-out from the module datasheet.
```
M check_courtyard_overlaps; M check_placement_clearance
M get_ratsnest / estimate_airwire_lengths           # long crossings = placement fix
M get_board_2d_view                                  # read the picture
M snapshot_project("placed")
```

## R6. Routing order
Hand-route in priority order. The autorouter is for whatever is left.
1. Diff pairs and controlled-impedance nets (USB, Ethernet, LVDS, RF) with
   `route_differential_pair`, then `validate_diff_pair_length_match`, then `add_meander` if needed.
2. Switching-regulator power loops and high-current paths: wide traces or pours, via arrays.
3. Clocks / crystals: short, no layer changes if you can avoid them.
4. Sensitive analog: away from switching nodes, with a guarded return path.
5. Everything else with `route_pad_to_pad`, or autoroute (R7).
Run `get_ratsnest(nets=[...])` after each group to prove it closed.

Never route a signal across a split or gap in its reference plane. Check with
K `check_return_path_continuity`.

## R7. Autoroute handoff
```
M snapshot_project("pre-autoroute")
M save_project; M is_dirty → false
K autoroute_pcb(passes=100, timeout_seconds=600)     # protects existing (hand) routes
M reload_board
M get_ratsnest                                        # remaining unrouted nets
K run_drc
```
If Freerouting leaves nets unrouted, don't just raise `passes`. Look at where they
are. Usually it's a placement bottleneck (a connector fan-out, or a QFN with no room
for vias), a missing via size in the netclass, or a clearance set too large for a
fine-pitch part. Fix that, then rerun.

## R8. Pours, stitching, fill
```
M add_copper_pour(layer=B.Cu (2L) or In1.Cu (4L), net=GND, outline=board, clearance, thermal)
(4L) power pour on In2.Cu split by rail where needed
M add_gnd_stitching_vias(spacing, edge rows)
K run_drc(refill_zones=true)                         # kicad-cli fill, avoids SWIG segfault
M reload_board
K analyze_ground_coverage; K check_return_path_continuity
```
On 2-layer boards, pour GND on both sides and stitch, and keep the bottom pour as
unbroken as routing allows.

## R9. DRC triage loop
```
M save_project
K run_drc(refill_zones=true, schematic_parity=true, severity="all")
```
Work the categories in this order. Each one can cause the ones after it:
1. **Parity** (footprint missing / extra / net mismatch): re-sync.
2. **Unconnected items**: route them, or find the unfilled zone.
3. **Shorts / clearance**: fix the geometry. Never loosen rules to clear a real violation.
4. **Hole / annular / edge clearance**: fab limits.
5. **Silk / courtyard**: cosmetic but real for assembly.
Use M `get_drc_violations` + `get_elements_in_region(x,y)` to localise, and
`get_board_2d_view` around it. Repeat until 0 errors. Every exclusion needs a stated reason.

## R10. Release package
```
M save_project
K run_drc(...) → 0/0                                  # final, on the saved file
M run_erc(root sheet) → 0 errors
K export_fab_package(include_render=true)             # gerbers/drill/pos/BOM/render
M export_ipc2581 / export_odb (industrial)
M export_ipcd356 (bare-board netlist test)
K export_step_3d                                      # enclosure check
M export_sch_pdf; M export_pcb_pdf (assembly drawing: F.Fab + F.Silk + Edge.Cuts)
K enrich_bom_with_sourcing (if keys) or M search_jlcpcb_parts per line
K export_pcb_svg per layer → look at copper + mask + silk
```
Sanity checks before you call it done: gerber layer count == copper layers + mask/paste/
silk/edge; drill file has both PTH and NPTH if there are mounting holes; BOM line count
== unique part groups; CPL has every SMD part with sane rotations (JLCPCB rotation
offsets differ for some packages, so flag that); board outline closed and on Edge.Cuts only.

Put a short `README`/fab-notes file next to the outputs: board name/rev/date, layer count,
thickness, copper weights, finish, mask/silk colours, impedance requirements with the
stackup, IPC class, and any special instructions.

## R11. ECO on an existing design
```
bash scripts/preflight.sh <dir>
M open_project; K set_project
python3 scripts/netlist_diff.py snapshot <root.kicad_sch> <workspace>/before.json
... schematic edits ...
python3 scripts/netlist_diff.py compare <root.kicad_sch> <workspace>/before.json   # changes must be exactly the intended ones
M sync_schematic_to_board                            # new footprints land near origin. Place them
route only the affected nets → DRC → bump revision in title block + silk
```
