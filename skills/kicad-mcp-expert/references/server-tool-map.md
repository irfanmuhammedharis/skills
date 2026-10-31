# Server & tool map

Which tool to reach for, per task. **K** = `mcp__kicad__*` (kicad-claude-mcp, Y-up,
file-based). **M** = `mcp__kicad-mixelpixx__*` (KiCAD-MCP-Server, Y-down, in-memory
board). ★ = preferred when both can do it.

Both servers expose many tools as deferred. Load the batch you need in **one**
`ToolSearch` call (`select:a,b,c`) at the start of each phase instead of one at a time.
mixelpixx also has `search_tools` / `list_tool_categories` / `get_category_tools` if
you can't remember a name.

## Contents
1. Project & session
2. Libraries & parts
3. Schematic
4. Board setup & rules
5. Placement
6. Routing
7. Zones, stitching, mechanical
8. Analysis & simulation
9. Verification
10. Outputs
11. GUI / live collaboration

---

## 1. Project & session
| Task | Tool | Notes |
|---|---|---|
| New project | ★M `create_project` then K `set_project` | M pins the session to SWIG on create. Point K at the same dir right away |
| Open existing | M `open_project` + K `set_project` | If the GUI has the same board open with IPC on, M pins to IPC (live sync) |
| What's loaded / dirty | M `get_backend_state`, `is_dirty`; K `get_project_state` | Check before every handoff |
| Save | M `save_project` | Refuses if disk changed externally. That's a feature: reload, don't force |
| Re-read after the other server wrote | M `reload_board` / `discard_or_reload` | |
| Checkpoint | M `snapshot_project` | Before autoroute, bulk moves, repairs |
| Multi-board project | K `add_board`, `set_active_board`, `list_boards` | All K PCB tools honour the active board |

## 2. Libraries & parts
| Task | Tool | Notes |
|---|---|---|
| Build search index (once, ~60 s) | K `index_libraries` | Needed before K `search_*` |
| Find symbol / footprint | ★K `search_symbol`, `search_footprint`, `get_symbol_details`; M `search_symbols`, `search_footprints`, `get_symbol_info`, `get_footprint_info` | Confirm pin numbering ↔ footprint pad numbering for every non-trivial part |
| Pins of a symbol | K `list_pins`; M `list_symbol_pins`, `batch_list_symbol_pins` | Batch version saves round trips for ICs |
| JLCPCB part (basic/extended, stock, price) | M `download_jlcpcb_database` (once), `search_jlcpcb_parts`, `get_jlcpcb_part`, `suggest_jlcpcb_alternatives` | Prefer Basic for prototypes |
| DigiKey / Mouser | M `digikey_search_parts`, `digikey_check_library_availability`; K `check_availability`, `enrich_bom_with_sourcing` | Needs API keys. If they're missing, say "stock unverified" |
| Datasheets | M `get_datasheet_url`, `enrich_datasheets` | Attach the Datasheet field for every active part |
| Vendor model (SnapEDA/UltraLibrarian zip) | K `import_vendor_zip`, `find_or_fetch_symbol`; M `import_symbol` | Then run M `repair_flat_symbols` (dry-run first) |
| Custom symbol / footprint | K `create_symbol`, `create_footprint` (auto courtyard/silk); M `create_symbol`, `create_footprint`, `edit_footprint_pad` | Register: M `register_symbol_library`, `register_footprint_library` |
| Validate a library | M `validate_symbol_library` | |

## 3. Schematic
| Task | Tool | Notes |
|---|---|---|
| New sheet | M `create_schematic`; hierarchy: M `add_hierarchical_sheet`, `create_hierarchical_subsheet`, `add_sheet_pin`, `add_schematic_hierarchical_label`; K `add_sheet`, `add_sheet_pin`, `add_hierarchical_label`, `set_active_sheet` | One sheet per functional block (power, MCU, I/O, comms) |
| Place + wire a block in one call | ★M `batch_add_and_connect` (`nets: {pin: NET}`, `labelType`) | Origins on 2.54 mm grid, ~12.7 mm spacing |
| Place only | M `batch_add_components`, `add_schematic_component`; K `add_symbol` (Y-up!) | |
| Connect | M `batch_connect`, `connect_to_net`, `add_schematic_wire`, `add_schematic_net_label`, `connect_passthrough` (connector↔connector); K `add_wire`, `add_label`, `add_power_symbol` | K wiring needs `get_pin_position` endpoints |
| No-connects | ★M `batch_add_no_connects`; K/M `add_no_connect` | Only on genuinely unused pins |
| Edit value/footprint/MPN/LCSC | ★M `edit_schematic_component` (`properties` map), `batch_edit_schematic_components`, `set_schematic_component_property` | Keeps UUID and position |
| Delete a wired part | M `delete_schematic_component` with `deleteAttachedLabels: true` | Otherwise orphan labels |
| Annotate | K `annotate_schematic` or M `annotate_schematic` | |
| Buses | K `add_bus`, `add_bus_entry`, `add_bus_alias` | |
| Inspect | M `list_schematic_components`, `list_schematic_nets`, `list_schematic_labels`, `get_schematic_pin_locations`, `get_wire_connections`, `list_floating_labels` | |
| Lint / repair | M `lint_offgrid` (`fix:true`), `find_orphaned_wires`, `find_wires_crossing_symbols`, `find_overlapping_elements`, `find_duplicate_symbols`, `repair_flat_symbols`, `validate_schematic` | |
| Tidy (netlist-safe) | M `lint_schematic_cosmetic` (`hide_pin_names`, `orient_labels`), `autoplace_schematic_fields`, `suggest_schematic_declutter` | Golden-netlist diff around it |
| See it | M `get_schematic_view`, `get_schematic_view_region`, `export_schematic_svg`/`export_sch_pdf` | Look at it |

## 4. Board setup & rules
| Task | Tool | Notes |
|---|---|---|
| Layer count / stackup | ★K `set_layer_count` (auto stackup); M `add_layer`, `set_layer_constraints` | **Before** any track or via on inner layers |
| Outline | ★M `add_board_outline` (rect / rounded / custom), `replace_board_outline`; K `set_board_outline` | |
| Fab rules | ★K `list_fab_presets`, `apply_fab_preset` (`jlcpcb_2l_default`, `jlcpcb_2l_advanced`, `pcbway_default`, `oshpark_4l`, `permissive_prototype`); M `set_design_rules`, `get_design_rules` | Presets are minimums. Production rules should sit above them |
| Netclasses | ★K `add_net_class`, `add_diff_pair_class`, `assign_net_class` (patterns), `list_net_classes`, `remove_net_class`; M `create_netclass`, `assign_net_to_class` | K writes `.kicad_pro` JSON directly, which survives M's save guard. Run M `reload_board` after |
| Custom DRC rules | ★K `add_drc_rule`, `list_drc_rules`, `remove_drc_rule`, `clear_drc_rules` (writes `.kicad_dru`) | Creepage, HV clearance, length/skew, keep-outs |
| Impedance targets | K `list_impedance_targets`, `solve_trace_width_for_impedance`, `calculate_*_impedance` | Fab stackup calculator is sign-off |
| Width for current | K `solve_trace_width_for_current`, `calculate_trace_current_capacity` | IPC-2152, state ΔT |

## 5. Placement
| Task | Tool | Notes |
|---|---|---|
| Bring schematic in (footprints + nets) | ★M `sync_schematic_to_board` | K `update_pcb_from_schematic` assigns nets only, no footprints |
| Initial spread | M `suggest_placement`, `hierarchical_place`; K `place_footprints_grid` | Starting point only. Then place deliberately |
| Move / rotate / flip | ★M `move_component`, `rotate_component`, `batch_move_components`, `align_components`, `group_components`, `place_component_array`; K `move_footprint` (Y-up) | Connectors and mechanical first, then ICs, then their passives |
| Check | M `check_courtyard_overlaps`, `check_placement_clearance`, `get_ratsnest`, `estimate_airwire_lengths`, `get_component_geometry`, `get_elements_in_region` | |
| Swap footprint | M `replace_component`, `edit_component`, `backannotate_footprints` | Keep schematic in sync |

## 6. Routing
| Task | Tool | Notes |
|---|---|---|
| Pad to pad | ★M `route_pad_to_pad` (auto net, auto via across layers) | Default choice for named pads |
| Free path / arcs | M `route_trace`, `route_arc_trace`; K `add_track` (Y-up) | |
| Diff pair | ★M `route_differential_pair`; K `list_diff_pair_candidates` | Then K `validate_diff_pair_length_match` |
| Length tune | K `add_meander`, `compute_trace_length` | |
| Vias | M `add_via`; K `add_via`, `add_via_array` (thermal / current) | |
| Autoroute | ★K `autoroute_pcb` (DSN→Freerouting→SES, Java 25 + bundled jar); M `check_freerouting`, `autoroute`; manual: K `export_dsn`/`import_ses` | M must `save_project` first and `reload_board` after |
| Copy a layout block | M `copy_routing_pattern` | Repeated channels |
| Edit / delete | M `modify_trace`, `delete_trace`, `query_traces` | |

## 7. Zones, stitching, mechanical
| Task | Tool | Notes |
|---|---|---|
| GND plane | K `add_ground_plane` (auto from outline); ★M `add_copper_pour`, `add_zone` | |
| Fill | K `run_drc(refill_zones=true)` (kicad-cli, safe) ★; M `refill_zones` (may segfault on SWIG) | |
| Stitching | M `add_gnd_stitching_vias`; K `add_ground_stitching` | λ/20 spacing at the highest relevant harmonic, plus along edges for EMC |
| RF line | K `add_rf_microstrip` | |
| Holes, fiducials | M/K `add_mounting_hole`; K `add_fiducial` | |
| Silk / logo | K `add_silk_text`; M `add_board_text`, `import_svg_logo` | |
| Panel | K `panelize_board_grid` | Or fab panelization service |

## 8. Analysis & simulation (all K, stateless, safe anytime)
`analyze_pcb_current_capacity`, `analyze_ground_coverage`, `check_return_path_continuity`,
`find_long_traces`, `validate_decoupling_caps`, `estimate_crosstalk`,
`simulate_thermal_steady_state`, `export_spice_netlist` + `run_ngspice_simulation`
(needs `Spice_*` fields and ngspice).

## 9. Verification
| Gate | Tool | Notes |
|---|---|---|
| ERC | K `run_erc` / M `run_erc` | Run on the **root** sheet for hierarchical designs |
| Netlist truth | M `generate_netlist` / `export_netlist`; K `export_netlist`; `scripts/netlist_diff.py` | |
| DRC | ★K `run_drc(refill_zones=true, schematic_parity=true)`; M `run_drc`, `get_drc_violations`, `kicad_run_drc` | K reads the file, so M saves first |
| Visual | M `get_board_2d_view`, `kicad_pcb_snapshot`; K `export_pcb_svg`, `render_pcb_3d` | |

## 10. Outputs
| Output | Tool |
|---|---|
| One-shot bundle | ★K `export_fab_package` (gerbers, drill PTH/NPTH, pos, BOM, render → `<proj>/fab/`) |
| Gerbers (full plot options) | M `export_gerbers` (X2, netlist attrs, DNP handling, subtract mask) |
| Drill | K `export_drill`; M `export_drill` |
| CPL / pos | M `export_pos` / `export_position_file`; K `export_pos` |
| BOM | M `export_bom`, `export_sch_bom`; K `export_bom` + `enrich_bom_with_sourcing` |
| Industrial data | M `export_ipc2581`, `export_odb`, `export_ipcd356`, `export_gencad` |
| 3D | K `export_step_3d`, `render_pcb_3d`; M `export_3d`, `export_3d_cli`, `export_vrml` |
| Docs | M `export_sch_pdf`, `export_pcb_pdf`, `export_pcb_dxf` (enclosure) |

## 11. GUI / live collaboration (M)
`launch_kicad_ui`, `check_kicad_ui`, `kicad_gui_screenshot`, `kicad_gui_click`,
`kicad_run_action_plugin`. IPC live sync needs KiCad running with
*Preferences → Plugins → Enable IPC API Server* and the board open **before**
`open_project`. Otherwise the session pins to SWIG and stays there.
