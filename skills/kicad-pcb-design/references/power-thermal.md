# Power Distribution, Thermal, and High Voltage

## Contents
1. Power integrity fundamentals
2. Decoupling strategy
3. Copper sizing and voltage drop
4. Vias for current
5. Thermal design
6. High current
7. High voltage, creepage and clearance
8. Protection

---

## 1. Power Integrity Fundamentals

- The PDN must present low impedance from DC to the highest frequency the load demands. DC is
  handled by copper cross-section, mid frequencies by bulk capacitance, high frequencies by
  local ceramics and plane capacitance.
- Build the rail budget as a table: rail, nominal V, tolerance, worst-case current, transient
  step, ripple allowance. Size converters at ≥1.3× worst-case current.
- Sequencing: check every IC's requirement (core before I/O, or a specified delay). An MCU whose
  I/O rail comes up first can latch up or back-power. Enforce with enable chains or a supervisor,
  not with luck.
- Feedback networks: sense at the load when it matters, route the feedback node short and away
  from the switch node, and never run it under the inductor.

## 2. Decoupling Strategy

- Per power pin: 100 nF X7R (0402/0603) at the pin, its own via to the plane, loop area
  minimised. Add 1 µF where the datasheet says so.
- Per device: 1–10 µF ceramic bulk near the device.
- Per rail entry / per converter: 10–100 µF (ceramic + electrolytic/polymer where ESR damping
  is needed).
- Derating is not optional: MLCCs lose capacitance under DC bias and with temperature — a
  6.3 V 10 µF 0402 X5R may deliver well under half its rating at 5 V. Choose voltage rating
  ≥2× the rail for small ceramics, and check the vendor's bias curve.
- Do not parallel many identical small values hoping for broadband performance; a couple of
  well-chosen values placed correctly beats a scattering of caps placed badly.
- Radio modules, ADCs, and PLL/VCO rails follow the app note's exact network (often
  ferrite + specific caps) — do not "simplify" it.

## 3. Copper Sizing and Voltage Drop

Use `pcb_calc.py trace-width` (IPC-2221 curve fit) for a first number and
`pcb_calc.py voltage-drop` for the DC drop; state the temperature rise you assumed (10 °C or
20 °C typical) and whether the trace is external or internal.

Indicative widths, 1 oz external copper, 10 °C rise:

| Current | Width |
|---|---|
| 0.5 A | ≈0.3 mm |
| 1 A | ≈0.6 mm |
| 2 A | ≈1.3 mm |
| 3 A | ≈2.2 mm |
| 5 A | ≈4.5 mm |

Internal layers need roughly twice the width for the same rise (worse cooling). These are DC
heating numbers only — they say nothing about voltage drop, which is often the binding
constraint on a long 3.3 V rail feeding a sensitive load. Above ~2–3 A prefer a polygon and
2 oz copper, and check the drop end to end.

## 4. Vias for Current

- A 0.3 mm drill, 25 µm plated via has roughly 1 mΩ of resistance and comfortably carries ~1 A
  with modest heating; compute with `pcb_calc.py via-current` and use several in parallel with
  margin (a via that also lives under a hot component runs hotter than the calculation says).
- Never neck a power net down to a single via; spread vias across the pad/polygon so current
  divides evenly.
- Vias in a thermal pad are both electrical and thermal — size for both, and fill/cap them if
  solder wicking would starve the joint.

## 5. Thermal Design

- Start from the numbers: P = losses per device (regulator: (Vin−Vout)×Iout for an LDO,
  (1−η)×Pout for a switcher), θJA from the datasheet *for the recommended board*, allowed
  Tj margin, ambient worst case. Then ΔT = P × θJA.
- Copper is the heatsink: a 2-layer board with a large top pour can dissipate roughly 1 W with a
  ~40–50 °C rise; a 4-layer board with thermal vias to inner planes does considerably better.
  Treat published θJA as optimistic unless your copper matches the datasheet's test board.
- **Thermal via arrays**: 0.3 mm drills on ~1.0–1.2 mm pitch under the pad, connected to a
  ground/plane pour on the far side (`pcb_calc.py thermal-vias` estimates the array's thermal
  resistance). Tent or fill them on the paste side to avoid solder loss.
- Heat spreads sideways poorly through FR-4 (≈0.3 W/m·K) and well through copper (≈390 W/m·K):
  the pour geometry *is* the heat path. Break the pour with a track and you break the heatsink.
- Keep electrolytics, crystals, batteries, and temperature sensors away from hot parts;
  electrolytic life roughly halves per 10 °C.
- Verify with measurement (thermal camera or a thermocouple) at bring-up and record the numbers
  in the design record; a thermal design that was never measured is a hypothesis.

## 6. High Current

- Polygons, not tracks, above ~2 A; 2 oz copper when the width becomes impractical (note the
  wider minimum trace/space that comes with it).
- Kelvin connections for shunt/current sense; sense traces routed as a pair away from the power
  path.
- Connectors: derate to ~50% of the datasheet rating per contact, parallel contacts for more,
  and check the wire gauge and crimp are part of the same budget.
- Fuses/PTCs sized for continuous current with derating at temperature; understand the inrush
  they must survive.
- Star the returns of high-current loads back to the source so their return current does not
  flow through signal ground regions.

## 7. High Voltage, Creepage and Clearance

- **Clearance** = shortest path through air; **creepage** = shortest path along the surface.
  Creepage is the larger requirement and depends on working voltage, pollution degree, and the
  material group (CTI). Use `pcb_calc.py creepage` for a first pass and verify against
  IEC 60664-1 / IPC-2221B tables for the actual product standard — the standard governs, not the
  calculator.
- Enforce in the tool with `creepage` and `clearance` rules on the mains netclass
  (design-rules-dru.md §4). KiCad 9+ has a real creepage constraint — use it rather than eyeballing.
- Slots milled under optocouplers, relays, and transformers extend the creepage path; specify
  them on `Edge.Cuts` and call them out in the fab notes.
- No copper, no silkscreen, no vias, and no traces crossing the isolation barrier. Solder mask is
  not insulation, and conformal coating changes the pollution degree only if the standard says so.
- Label the hazard region on silkscreen; keep test points off the primary side unless the fixture
  is designed for it.

## 8. Protection

- Reverse polarity: P-channel MOSFET (low drop) or a series diode where the drop is acceptable.
- Overvoltage/transients: TVS at the input, rated for the surge class the product must survive;
  place it before anything else on the path.
- ESD on every external interface, at the connector, low capacitance for high-speed lines,
  with a short low-inductance return to chassis ground.
- Inrush: NTC or soft-start for large bulk capacitance, especially on hot-plug connectors.
- Inductive loads (relays, motors, solenoids): flyback diodes or snubbers on the board, with the
  loop kept tight and away from logic.
- Every protection component's *return path* is part of the protection — a TVS with a long thin
  ground trace does very little.
