# Industrial / production tier

Use for anything going into a product, the field, a certification lab, or volume
assembly. The aim is that a contract manufacturer can build it from your package
with no questions, and it survives the test lab and five years in a cabinet.

Walk this checklist at gate 7. Mark each item PASS / N/A (reason) / WAIVED (who, why).
Present the result as a table.

## Contents
1. Architecture & parts
2. Power entry & protection
3. Interfaces (industrial I/O)
4. Isolation, creepage, clearance
5. Stackup & SI
6. Thermal
7. EMC layout
8. DFM
9. DFT
10. Documentation & release

---

## 1. Architecture & parts
- [ ] Every non-passive part: lifecycle **Active**, not NRND/EOL. Second source identified
      (pin-compatible or footprint-compatible alternate in the BOM `Alt_MPN` field).
- [ ] Temperature grade covers the spec (industrial −40…+85 °C; automotive AEC-Q100/200).
- [ ] Derating: capacitor V ≥ 1.5× (ceramic ≥ 2×, account for DC-bias loss), electrolytic
      ripple and lifetime at max ambient, resistor P ≤ 50 %, semiconductors Tj ≤ 80 % of max.
- [ ] MLCC ≥ 1206 not placed near board edges, V-score lines or connectors (flex cracking),
      or use soft-termination parts.
- [ ] Watchdog/supervisor/brown-out reset on the MCU rail.
- [ ] Datasheet field populated for every active part.

## 2. Power entry & protection (in this order from the connector)
- [ ] Fuse / PTC / eFuse sized for fault current and wire gauge.
- [ ] Reverse polarity: series Schottky (simple), P-FET ideal diode, or eFuse with RP.
- [ ] TVS sized to the surge spec (IEC 61000-4-5 level, or ISO 7637/16750 for vehicles):
      standoff above max operating V, clamp below downstream abs-max. Check its
      peak pulse power against the waveform.
- [ ] Input bulk + bulk-cap inrush handled (hot-plug ringing on 24 V lines with ceramics only).
- [ ] UVLO / OVLO where the input range is wide.
- [ ] Each regulator: input/output caps per datasheet at derated capacitance, thermal checked
      (`K simulate_thermal_steady_state`), soft-start, PG used if available.

## 3. Interfaces (industrial I/O)
- [ ] ESD on every externally reachable pin (IEC 61000-4-2 ±8 kV contact minimum), TVS at
      the connector, with a short, low-inductance path to chassis/GND.
- [ ] RS-485/CAN: transceiver with fault-tolerant bus pins, split termination with a
      bias network, common-mode choke if the spec needs it, TVS rated for the bus, and
      isolation if long cables or ground-potential differences are expected.
- [ ] 24 V digital inputs: IEC 61131-2 type 1/3 thresholds, current limiting, optional
      isolation. Outputs: high-side switch with short/thermal protection and inductive
      kickback handled.
- [ ] 4–20 mA: burden resistor tolerance/tempco, loop protection, ADC reference stability.
- [ ] Shield/chassis strategy decided and documented (e.g. 1 nF/2 kV + 1 MΩ to GND at entry).

## 4. Isolation, creepage, clearance
- [ ] Working voltage, overvoltage category, pollution degree and material group stated.
- [ ] Creepage/clearance from IEC 62368-1 or 60664-1 tables, encoded as
      `K add_drc_rule` constraints between net classes (e.g. `HV` ↔ `SELV`) so DRC enforces it.
- [ ] Isolation barrier: no copper on any layer crossing it, slot under optocouplers or
      isolators if needed, isolated DC/DC rated for the test voltage.
- [ ] Mains-connected areas marked on silk.

## 5. Stackup & SI
- [ ] 4 layers minimum when there's MCU + switching power + any interface above a few MHz
      (SIG / GND / PWR / SIG, or SIG / GND / GND / SIG for EMC-critical designs).
- [ ] Fab-specific stackup chosen (e.g. JLCPCB JLC04161H-7628) and documented. Impedance
      widths re-derived with `K solve_trace_width_for_impedance` against **that**
      stackup, with fab calculator / impedance-control order as sign-off.
- [ ] Diff pairs: length-matched within spec (`K validate_diff_pair_length_match`),
      continuous reference plane, ≤ 2 vias per signal, GND return vias next to signal vias.
- [ ] Crosstalk on long parallel runs checked (`K estimate_crosstalk`), 3W rule for clocks.

## 6. Thermal
- [ ] Every part dissipating > ~0.25 W: Tj estimated with the real copper area (`K
      simulate_thermal_steady_state`). Thermal via array under EP (0.3 mm drill, 1–1.2 mm
      pitch, tented or plugged per assembler).
- [ ] Power traces IPC-2152 sized at the stated ΔT (`K analyze_pcb_current_capacity`).
- [ ] Hot parts away from electrolytics, crystals and temperature sensors.

## 7. EMC layout
- [ ] Unbroken GND reference under every signal (`K check_return_path_continuity`).
- [ ] Switching loops minimal. SW node copper as small as current allows. No signals under inductors.
- [ ] Decoupling validated (`K validate_decoupling_caps`).
- [ ] No long unterminated traces acting as antennas (`K find_long_traces`).
- [ ] Edge stitching vias (λ/20 at the highest harmonic of concern) and GND pour on outer layers,
      tied to inner GND (`K analyze_ground_coverage`).
- [ ] Filtering (ferrite/π) on cables leaving the box. Connectors grouped on one edge where possible.

## 8. DFM
- [ ] Rules **above** fab minimums (e.g. 0.15/0.15 mm on a 0.127 mm process) to keep yield up.
- [ ] Annular ring, hole-to-copper, copper-to-edge per fab. Via-in-pad only with filled+capped vias ordered.
- [ ] Paste aperture reductions on large EPs (windowpane, ~50–70 % coverage).
- [ ] Single-sided SMT if achievable. Otherwise heavy parts only on top.
- [ ] Fiducials: 3 global per side carrying parts, plus local pairs at fine-pitch (≤ 0.5 mm) ICs
      (`K add_fiducial`, 1 mm copper, 2 mm mask opening).
- [ ] Panel: rails + tooling holes + fiducials on rails (fab service or `K panelize_board_grid`),
      mouse-bites away from MLCCs and connectors.
- [ ] Silk: ≥ 1.0 mm text / 0.15 mm stroke, off pads, polarity marks on every polarised part, pin-1
      marks, board name + rev + date code box + regulatory marks.
- [ ] Courtyards clean, component-to-component spacing OK for the reflow and AOI process.

## 9. DFT
- [ ] Test point on every power rail, reset, boot, programming/debug lines, and each
      interface's bus lines, plus every net the ICT fixture needs (`TestPoint` symbols so
      they appear in CPL).
- [ ] TP pads ≥ 1.0 mm, ≥ 2.54 mm pitch for bed-of-nails, all on one side.
- [ ] Programming via pogo-pin footprint (Tag-Connect or pad pattern) rather than a populated header.
- [ ] A serial number / MAC storage plan (EEPROM, MCU OTP, or label area).
- [ ] FCT plan: list what each test proves.

## 10. Documentation & release
- [ ] Revision in title block, silk and output folder name (e.g. `fab/<name>-rev-B-2026-10-28/`).
- [ ] Outputs: Gerber X2 + drill (PTH/NPTH) **or** IPC-2581/ODB++, IPC-D-356 netlist,
      CPL, BOM (MPN, manufacturer, alternates, DNP flags), STEP, schematic PDF, assembly
      drawing PDF, fab-notes (stackup table, impedance, IPC class, finish, colours,
      thickness, special processes).
- [ ] DRC 0 errors / 0 unconnected on the **saved** file. Exclusions listed with reasons.
- [ ] ERC 0 errors on the root sheet.
- [ ] Design-review record: this checklist plus open risks and their owners.
- [ ] Project snapshot/tag at release (`M snapshot_project("rev-B release")`, plus git if the
      user uses it).
