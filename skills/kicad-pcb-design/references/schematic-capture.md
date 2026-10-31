# Schematic Capture

The schematic is the contract. Every layout error that survives review started as a schematic
that was readable but not *reviewable*.

## Contents
1. Before drawing: block diagram and power tree
2. Sheet structure and hierarchy
3. Drawing conventions that make review possible
4. Connectivity: labels, buses, power symbols, jumpers
5. Component selection and field discipline
6. Annotation and ERC
7. Variants and DNP
8. Schematic → PCB transfer

---

## 1. Before Drawing: Block Diagram and Power Tree

Produce first, in the design record:

- **Block diagram**: functional blocks, the buses between them, and which sheet each becomes.
- **Power tree**: source → each converter → each rail, with for every rail: voltage, tolerance,
  max current (sum of worst-case loads, not typicals), sequencing requirement, and quiescent
  budget if battery powered. Add 30% headroom on converter selection.
- **Interface list**: every connector, its pinout, mating part, and what protection it needs.
- **MCU pin budget**: assign peripherals to pins now, checking the datasheet's alternate-function
  table — including boot-strapping pins, ADC-capable pins, and pins unusable while flashing.
  ESP32 family: respect strapping pins (IO0/IO2/IO12/IO15 on classic ESP32), the flash pins,
  and input-only GPIO34–39.

Doing this after the schematic is drawn means redrawing the schematic.

## 2. Sheet Structure and Hierarchy

- One sheet per functional block: `power.kicad_sch`, `mcu.kicad_sch`, `sensors.kicad_sch`,
  `io.kicad_sch`. Root sheet = block diagram made of sheet symbols and the buses between them.
- Sheet size A4/A3, consistent across the project; title block filled (project, sheet name,
  rev, date, author) using text variables.
- Signal flow left→right, power top, ground bottom. A reviewer should be able to trace a signal
  without panning backwards.
- Repeated channels: one sheet instantiated N times (multi-instance hierarchical sheets), so
  fixing the channel fixes all of them — and pairs with layout replication later.

## 3. Drawing Conventions That Make Review Possible

- No overlapping wires that are not connected; junctions explicit. KiCad 10's hop-over display
  makes crossings unambiguous — turn it on.
- Nothing hidden: no invisible power pins doing secret work. If a symbol has hidden power pins,
  make them visible or use explicit power flags so the reviewer sees the connection.
- Group parts with the function they serve: decoupling caps beside their IC pins on the sheet,
  not in a "capacitor farm" corner. Layout follows schematic organisation.
- Annotate intent in text: "10 k pull-up required by I²C spec at 400 kHz with 100 pF bus",
  "R7 sets ILIM to 1.5 A", "DNP unless using external antenna". Future-you and the reviewer are
  the audience.
- Values written unambiguously: `100n` or `100nF`, `4k7`, `0R`; add tolerance/voltage/dielectric
  in fields (a 100 nF X7R 50 V and a Y5V 6.3 V are not the same part).

## 4. Connectivity: Labels, Buses, Power Symbols, Jumpers

- **Local labels** stay within a sheet. **Hierarchical labels** cross into the parent sheet
  through sheet pins. **Global labels** are for genuinely board-wide nets only — over-use makes
  connectivity invisible.
- Name nets for function: `VBUS`, `+3V3_MCU`, `SPI1_SCK`, `SENS_TEMP_AN`. Suffix analog nets and
  differential pairs correctly: KiCad pairs by `_P`/`_N` (also `+`/`-`) suffix on a common base
  name — required for diff-pair routing and `inDiffPair()` rules.
- Power symbols define nets by their *name*, not by the graphic. Two different symbols named
  `+3V3` are the same net; a symbol named `+3.3V` is a different net. Standardise once.
- `PWR_FLAG` only where a supply enters the board with no driving output pin; it silences ERC's
  "no driver" — never sprinkle it to mute real errors.
- No-connect flags on every genuinely unused pin. An unflagged unused pin is indistinguishable
  from a forgotten one.
- **Jumpers** (KiCad 10): declare pins/pads that are internally connected (solder bridges,
  off-board links, zero-ohm options) so they share a net and produce no ratsnest — the correct
  way to model shorting links instead of fake nets.

## 5. Component Selection and Field Discipline

Every symbol carries, as fields, at release: `Reference`, `Value`, `Footprint`, `Datasheet`,
`MPN`, `Manufacturer`, `Description`, supplier PN (`LCSC` for JLCPCB assembly), plus as needed
`Tolerance`, `Voltage`, `Power`, `Dielectric`, `Temperature`.

- Choose parts that are *in stock in the quantity you need* before the schematic is frozen; a
  perfect design around an unobtainable part is a delay, not a design. Check the assembler's
  parts library (e.g. JLCPCB basic vs extended parts) — a basic-part alternative saves setup fees.
- Passive derating: ceramics lose capacitance with DC bias (an 0402 10 µF 6.3 V X5R at 5 V may
  deliver <3 µF) — pick the voltage rating for the capacitance you need, not just for survival.
  Resistors ≤50% of rated power; electrolytics rated for ripple current and temperature.
- Prefer packages your assembly process can handle: 0402 minimum for hand work, 0603 comfortable;
  fine-pitch BGA changes the fab class and cost.
- Every IC: read the datasheet's application section for required externals (bulk vs bypass
  values, ferrite on the analog rail, minimum ESR, reset/enable pull-ups, boot sequencing).

## 6. Annotation and ERC

- Annotate by sheet, keeping refdes ranges per block (100s = power, 200s = MCU …) — makes
  assembly documentation and board debugging readable.
- Run ERC to zero: unconnected pins, conflicting outputs, missing power inputs, unresolved
  hierarchical labels, duplicate refdes, mismatched footprint assignments, missing fields
  (custom ERC on required fields).
- Exclusions are documented, not silent: an excluded ERC item without a written reason is a bug
  waiting to be re-found in review.
- CLI: `kicad-cli sch erc --severity-all --exit-code-violations --format json -o erc.json x.kicad_sch`.

## 7. Variants and DNP

- `DNP` marks a symbol as not populated; `Exclude from BOM` removes it from purchasing;
  `Exclude from board` removes it from the PCB netlist. These are three different statements —
  set them deliberately.
- Use DNP for deliberate options (alternate resistor values, unpopulated debug headers), never
  to hide unfinished work.
- KiCad 10 **variants**: define named variants with per-variant field/fit differences, then
  export per-variant BOM/CPL/plots with `--variant <name>`. This replaces the old habit of
  maintaining parallel schematics — which always drift.

## 8. Schematic → PCB Transfer

- Update PCB from Schematic: match by reference or by unique ID (UUID matching survives
  re-annotation; use it). Review the change list before applying — it tells you exactly what the
  schematic just did to the board.
- After any schematic change, re-run **DRC with schematic parity**
  (`kicad-cli pcb drc --schematic-parity …`); it catches nets and footprints that drifted apart.
- Back-annotation: pin/gate swaps done in the PCB (KiCad 10 supports unconstrained pin/pad and
  gate/unit swaps with forward and back annotation) must be pushed back so the schematic remains
  the truth. Never leave the board as the only place a swap is recorded.
