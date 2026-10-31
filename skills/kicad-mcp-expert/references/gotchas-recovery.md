# Gotchas & recovery

Symptom → cause → fix. Most of these come from the servers' own known-issues docs
(`~/KiCAD-MCP-Server/docs/KNOWN_ISSUES.md`, `HEADLESS_AUTHORING.md`,
`~/kicad-claude-mcp/README.md` caveats). Re-read those if a symptom isn't listed here.

Ground-truth rule: **kicad-cli (ERC/DRC/exports) beats kicad-skip editing tools.**
If `kicad-cli sch export svg` renders a file, the file is valid KiCad, whatever a skip
tool says.

---

### Edits vanish / "save refused: file changed on disk"
- **Cause:** two writers. Either `kicad` wrote the `.kicad_pcb` while mixelpixx held it
  in memory, or the KiCad GUI has it open.
- **Fix:** don't `save_project(force:true)`. Decide which copy is right. If it's disk:
  `M reload_board`. If it's mixelpixx memory, the other edit is lost anyway, so redo it
  after saving. Close the GUI before file edits (preflight reports `~*.lck` files), or
  work IPC-pinned.

### Parts land mirrored vertically / off the page
- **Cause:** a Y-up coordinate (from `kicad`) passed to mixelpixx, or the reverse.
- **Fix:** `scripts/coord.py`. Pick one server for all placement in a session.
- **Also:** on portrait, User-size or US A–E sheets, kicad-claude-mcp flips with the wrong
  height (it uses the landscape table and defaults to 210 mm), so its positions are offset
  even after conversion. `coord.py --file` warns about this. Use mixelpixx for placement there.

### Board has nets but no footprints (or footprints but no nets)
- **Cause:** used `K update_pcb_from_schematic` (nets only) on an empty board, or the
  symbols had no `Footprint` field.
- **Fix:** give every symbol a footprint (`M edit_schematic_component`), then
  `M sync_schematic_to_board`. Check with `M get_component_list`.

### `schematic_load_failed` with `flatSymbols: [...]`
- **Cause:** a SnapEDA/SamacSys symbol without a `_1_1` sub-unit. kicad-skip can't parse it.
- **Fix:** `M repair_flat_symbols` (dry-run, then apply) on the `.kicad_sym` **and** on
  every `.kicad_sch` that embeds a copy in `lib_symbols`.

### Junctions missing / pins "connected" but ERC says unconnected / weird sheet-wide errors
- **Cause:** something off the 1.27 mm connection grid (one stray origin can poison the
  whole sheet).
- **Fix:** `M lint_offgrid(fix:true)`. Keep symbol origins on 2.54 mm. Leave field-text
  positions alone. They're cosmetic.

### ERC `pin_not_driven` / `power_pin_not_driven`
- Rail fed from a connector or passive → add one `PWR_FLAG` on the originating sheet.
- Global-label design checked per sheet → re-run ERC on the **root** sheet. Per-sheet
  undriven warnings on cross-sheet inputs are expected.
- Vendor regulator output typed `passive` → PWR_FLAG.
- `Power output and Power output are connected` → you have one flag too many.

### ERC `missing_power_pin` on 74xx / quad op-amps
- Place the separate power unit of the symbol.

### Exposed pad errors (`pin_not_connected` on EP)
- Tie EP to its datasheet net (usually GND) and give it a thermal via array on the footprint.

### `label_dangling` after deleting a part
- `M delete_schematic_component(deleteAttachedLabels:true)`. For leftovers: `M list_floating_labels`.

### Zones show unfilled / DRC reports unconnected GND everywhere
- **Cause:** SWIG zone filler not run (or it segfaulted).
- **Fix:** `K run_drc(refill_zones=true)` fills via kicad-cli and saves. Then `M reload_board`.
  Opening in the GUI also fills.

### Netclass / net settings revert after saving
- **Cause:** pcbnew re-serialises `.kicad_pro` on board save. mixelpixx's guard restores
  on-disk `net_settings`, so model-side netclass changes get reverted on purpose.
- **Fix:** set netclasses with `K add_net_class` / `assign_net_class` (direct JSON edit),
  then `M reload_board`. Verify with `K list_net_classes`.

### Inner-layer tracks become orphans / DRC "item on disabled layer"
- `set_layer_count` ran after copper was placed on inner layers. Set layer count first.
  To recover, delete the orphaned items and re-route.

### Freerouting leaves nets unrouted / times out
- Check `java -version` (bundled jar 2.1.0 works on Java 21–25). For the M path, run `check_freerouting`.
- Unrouted nets cluster where placement is too tight: fix placement, add via room,
  check the netclass via size fits fine-pitch fan-out, and lock hand-routed critical nets.
- Very large boards: raise `timeout_seconds` rather than `passes` first.

### `get_board_info` → `'BOARD' object has no attribute 'LT_USER'`
- Known KiCad 9+ API change. Use `M get_project_info`, `get_layer_list`, `get_board_extents`.

### Symbol with `extends` (e.g. `Device:R_Small`) breaks in `K add_symbol`
- K injects only the derived symbol. Use the base (`Device:R`), or place it with M.

### Tool call hangs, then every later reply looks wrong
- An old mixelpixx bridge bug (fixed in 2.7). If you see off-by-one replies, restart the
  server and `open_project` again. After any server restart, the board reference is
  gone, so re-open it.

### IPC never activates
- Needs KiCad running, *Enable IPC API Server* on, the **same** `.kicad_pcb` open in
  pcbnew, and `open_project` called **after** that. `create_project` always pins SWIG.
  Check `/tmp/kicad/api.sock` and `M get_backend_state`.

### `kicad-cli: Failed to load schematic` right after a tool edit (file unloadable, tool said "success")
- **Cause (seen):** mixelpixx `add_schematic_text` with `justify: "center"` writes `(justify center bottom)`
  verbatim. KiCad has no `center` token (centred is the default when `justify` is omitted), so the whole
  schematic stops loading. Every later kicad-cli step (ERC, netlist, export) then fails.
- **Fix:** replace the token (`sed -i 's/(justify center bottom)/(justify bottom)/'`), or omit `justify`.
  Valid tokens are only `left right top bottom mirror`. Use them in hand-written text too.
- **Prevention:** after *every* tool that writes a `.kicad_sch`, run
  `kicad-cli sch export netlist --format kicadxml -o /dev/null <sch>` (or `netlist_check.py`). Keep a copy before
  risky edits. To find the bad item, bisect: strip one top-level element type at a time and retry the load.

### Title block vanishes after `batch_edit_schematic_components` / other re-saving tools
- **Cause:** the tool re-serialises the sheet and drops `(title_block ...)`.
- **Fix:** insert the title block **last**, after all tool edits, then re-check it is present
  (`grep -c '(title_block'`). Note the file is tab-indented after a tool save, so match `\s*(paper "A3")`
  with a regex; a literal-space `str.replace` silently matches nothing.

### Stale `~name.kicad_sch.lck` / `~name.kicad_pro.lck` left in the project
- **Cause:** the mixelpixx session creates them on `create_project`/`open_project`; `close_project` does not
  always remove them. The KiCad GUI then warns "file is already open", and preflight reports a FAIL.
- **Fix:** `close_project(save:false)` first (so the server can't write over finished files), confirm
  `pgrep -x kicad` finds nothing, then delete the two `.lck` files. They only contain hostname/username.

### Hand-writing wires, junctions and graphics straight into the `.kicad_sch`
- This is fine, and much faster than ~60 single-wire calls: wires, `(junction ...)` dots and non-electrical
  `(polyline)`, `(rectangle)`, `(circle)`, `(text)` items are all ordinary top-level items inserted before
  `(sheet_instances`. Rules that kept it safe: use exact pin coordinates from `get_schematic_pin_locations`;
  put a vertex on every tap of a rail; add a junction wherever 3+ ends meet; never let two nets' wires touch;
  keep a backup; make the insert script refuse to run twice (guard on a string unique to your items, **not**
  `(rectangle`, which also appears inside library symbols); then prove it with `kicad-cli` load + ERC +
  `netlist_check.py`.

### Two writers raced: "Auto-save refused: the on-disk PCB file's contents changed externally"
- **Seen when:** `add_board_outline` and `sync_schematic_to_board` were sent in the same parallel batch. Both are
  mixelpixx, but sync writes the file through a separate pcbnew process, so the two collide.
- **Fix:** don't force. Inspect the disk file (footprints, outline), `reload_board`, then redo only what is missing.
  **Prevention:** `sync_schematic_to_board`, `autoroute_pcb`, `update_pcb_from_schematic`, `run_drc(refill_zones)`
  each write the whole board, so run them alone, one at a time, with a save and a clean `is_dirty` before and a
  `reload_board` after.

### Parity DRC shows ~80 `net_conflict` warnings (`Net-(D1-Pad1)` vs `Net-(D1-K)`, `LOW` vs `/LOW`)
- **Cause:** mixelpixx `sync_schematic_to_board` names unlabelled nets by pad number and drops the `/` that kicad-cli
  puts on local-label nets, so the PCB's net names differ from the schematic's.
- **Fix, before routing:** after the sync, run `kicad: update_pcb_from_schematic`. It re-assigns every pad to the
  schematic's own net names (parity then shows 0 net conflicts). Do it *before* autoroute: tracks keep the old net
  code, so renaming afterwards leaves tracks on nets with no pads. If you are already routed, restore the board
  backup that `autoroute_pcb` writes to `.backups/` and redo the sequence.
- Netclass patterns must use the post-rename names (`+9V` and `GND` stay un-prefixed because they come from power symbols).

### `kicad: set_project` errors (`'PCB' object has no attribute 'net'` or `'Symbol' object has no attribute '_base_coords'`)
- It sets the active project *before* the parse that fails, so `add_net_class`, `assign_net_class`,
  `apply_fab_preset`, `update_pcb_from_schematic`, `autoroute_pcb`, `run_drc` and `export_*` still work, but
  `get_project_state` / `list_components` fail. Confirm where a write landed by reading that project's `.kicad_pro`
  (and `find -mmin`) instead of trusting the call.

### Netclass clearance larger than the footprint's own pad gap, so DRC errors on every transistor
- A TO-92 has 0.22 mm between pads; a 0.25 mm class clearance fails on each one. Keep class clearance at or below
  the tightest part you use (0.2 mm), or add a `pad_to_pad` floor rule. Fix the rule, never the placement.

### `add_mounting_hole` writes an unusable library id
- It creates `MountingHole:MountingHole_3.2mm`, which doesn't exist (DRC: "not found in library"). Delete those and use
  `place_component` with the real `MountingHole:MountingHole_3.2mm_M3`. Hide the Reference text of the holes (it sits on
  silk past the board edge and gets clipped). The 4 holes then appear in parity as `extra_footprint`, which is expected
  for board-only mechanical parts.

### `kicad: export_fab_package` is not release-grade
- It writes ~25 gerber layers (Courtyard, Fab, Margin, User_*, Adhesive, Comments, Eco) that fabs do not want, and in
  one run mis-grouped BOM lines. Use it for BOM/CPL/render, but build the gerbers with
  `kicad-cli pcb export gerbers --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"`
  and `kicad-cli pcb export drill --format excellon --drill-origin absolute --excellon-separate-th --generate-map`,
  then verify hole counts (pads + vias) and the outline extents from the files.

### `get_nets_list` shows every net as class `Default`
- Reporting quirk. Judge the netclass by the `.kicad_pro` patterns and the routed track widths.

### A big `batch_add_*` call timed out and left the schematic at 0 bytes
- Seen with ~40 parts in one call. Keep batches to ~15 parts, back the file up before each batch, and re-run the
  load check after every one.

### Logs
- mixelpixx: `~/.kicad-mcp/logs/kicad_interface-<pid>.log` (dev mode: `KICAD_MCP_DEV=1`).
- kicad-claude-mcp: stderr of the server process. Raw ERC/DRC JSON paths come back in
  `run_erc` / `run_drc` results. Open them when the summary is ambiguous.
