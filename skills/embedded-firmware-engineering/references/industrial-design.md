# Industrial Electrical Design: 24 V Systems, I/O Interfaces, EMC Immunity

The industrial environment runs on 24 VDC, long cables, motor noise, and surge events. Consumer-design habits fail here. This file complements circuit-design.md (general design) with the industrial layer.

## Contents
1. 24 VDC power architecture
2. Industrial digital inputs/outputs (IEC 61131-2)
3. Analog I/O: 4–20 mA and 0–10 V
4. Galvanic isolation design
5. EMC immunity design (IEC 61000-4-x)
6. Environmental hardening
7. Connectors and wiring practice
8. Hazardous areas (ATEX/IECEx) awareness

---

## 1. 24 VDC Power Architecture

- Input range: design for 18–30 V (nominal 24 V, ±20% + dips); hold-up through 10 ms dips (IEC 61131-2 PS2 or site spec) — bulk capacitance or active hold-up, show the energy math.
- Wide-input buck (36–60 V max input rating) to an intermediate rail (5 V or 3.3 V); never run MCUs off an LDO from 24 V (dissipation: 20.7 V × I — see circuit-design.md §2).
- Input protection chain: fuse/PTC → reverse-polarity MOSFET → TVS (33–36 V standoff, sized for surge per §5) → EMI filter (common-mode choke + caps) → buck. This chain is standard industrial practice — omit stages only with justification.
- Inrush: hot-plugging into live 24 V rails — input cap charging spike kills connectors and trips supplies; add NTC/active inrush limiting if capacitance is large.

## 2. Industrial Digital Inputs/Outputs (IEC 61131-2)

**Inputs (Type 1/2/3):** 24 V logic levels, thresholds per type (e.g., Type 3: ON >11 V, OFF <5 V). Circuit: divider + RC filter (1–10 ms debounce region) + clamp → optocoupler or comparator with hysteresis → MCU. Never connect 24 V field wiring to MCU pins through a bare divider — one surge and the board is gone.
- Sink vs. source (PNP/NPN sensor outputs) — support what the spec says; state it on the connector label.

**Outputs:**
- High-side switches (e.g., ITS/IPS series, protected high-side drivers) for sourcing outputs: built-in current limit, thermal shutdown, diagnostics (open-load, short) — the diagnostics are why you use them instead of a bare MOSFET.
- Short-circuit tolerance is mandatory: field wiring gets shorted; the output must survive and report, not burn.
- Relay outputs for galvanic switching of mixed loads: derate per actuators-power-hmi.md §1, arc suppression for inductive loads.
- Every output: defined power-on/reset state (OFF), watchdog-supervised for hazards (reliability-testing.md §1).

## 3. Analog I/O: 4–20 mA and 0–10 V

- 4–20 mA is the industrial standard because: current is immune to voltage drop/noise over long runs, 4 mA = live zero (0 mA = broken wire detection — always implement wire-break diagnostics).
- Input circuit: precision shunt (e.g., 100–165 Ω → 0.4–2 V or per ADC range) → overvoltage/overcurrent protection (PTC + clamp) → ADC; accuracy budget: shunt 0.1% + ADC + reference (circuit-design.md §5). Loop-powered vs. 4-wire transmitters differ in where power comes from — know which you're interfacing.
- Output: dedicated DAC/current-output IC (e.g., XTR111-class or DAC + V/I stage); compliance voltage across the loop supply range.
- 0–10 V outputs: buffer op-amp, short-circuit protected, defined behavior into open load.
- HART (digital overlaid on 4–20 mA): modem IC (e.g., AD5700-class) if spec'd — it's FSK on the loop; the analog path must not filter it away.

## 4. Galvanic Isolation Design

- Where: field-side I/O vs. logic, RS-485/CAN segments across power domains, mains-adjacent anything, sensor loops in noisy plants.
- Isolators: digital isolators (capacitive/magnetic — ADuM, ISO77xx) over optocouplers for speed/lifetime; isolated DC/DC (1–2 W modules) to power the field side; or integrated iso-power isolators.
- Ratings: working voltage, isolation rating (2.5–5 kVrms), CMTI (common-mode transient immunity — matters with fast switching nearby), creepage/clearance on the PCB across the isolation barrier (slot the board, no copper under the barrier — see pcb-layout.md §7).
- The isolation barrier is a system feature: every signal and every power path crossing it enumerated; a single non-isolated crossing defeats it.

## 5. EMC Immunity Design (IEC 61000-4-x)

Industrial certification tests your design must survive — design FOR them, then pre-test:

| Test | Standard | Level (typ. industrial) | Design measures |
|---|---|---|---|
| ESD | 61000-4-2 | ±4 kV contact / ±8 kV air | TVS at every connector, chassis-ground ESD path (pcb-layout.md §3) |
| EFT/burst | 61000-4-4 | ±1–2 kV on I/O | Input filtering, isolation, firmware recovery (re-init peripherals — reliability-testing.md §4) |
| Surge | 61000-4-5 | ±1–2 kV line-earth | Proper TVS/GDT/MOV coordination — device must clamp and survive energy, not just spike |
| Conducted RF | 61000-4-6 | 3–10 V, 150 kHz–80 MHz | CM chokes on ports, filtered inputs; firmware plausibility checks on all readings |
| Power dips | 61000-4-11/29 | dips/interruptions | Hold-up energy (§1), brown-out discipline, safe-state |
| Radiated RF | 61000-4-3 | 3–10 V/m | Enclosure/shielding, layout discipline |

- Firmware's role in EMC pass: the device may glitch but must not latch-up, corrupt, or misbehave — watchdog, peripheral re-init, RAM integrity checks, plausibility rejection. Class B performance (self-recovery) vs. Class A (no deviation): state the target.
- Pre-compliance: rent time on an ESD gun and burst generator before the lab — fixes are 10× cheaper.

## 6. Environmental Hardening

- Temperature: industrial −40…+85 °C component grade end-to-end (capacitor lifetime math at max ambient — circuit-design.md §7); conformal coating for humidity/contamination (note: coating complicates rework and probe access — plan test points).
- IP rating is enclosure + connectors + cable glands: electronics must survive condensation inside "sealed" enclosures (breather vents, conformal coat).
- Vibration (IEC 60068-2-6): no tall heavy parts on thin solder only (glue/stake large caps, connectors with locking), strain-relief on all cables, no socketed parts in high-vibration.
- MTBF thinking: electrolytic-free design where possible (polymer/ceramic), derating per circuit-design.md §7 — industrial customers ask for MTBF numbers; be ready with component-fit calculations (SN 29500 / MIL-HDBK-217 awareness).

## 7. Connectors and Wiring Practice

- Industrial standards: M12 (A-coded sensors, D-coded Ethernet), M8, push-in/spring terminal blocks for power/I/O — never pin headers to the field.
- Terminal block layout: group by function, power at edges, clear labeling (24V/0V/IO numbers matching the manual); wire ferrules assumed.
- Strain relief and locking on everything; shield continuity through connector shells where shielded cable is used.
- DIN-rail (35 mm) mounting for control-cabinet products — design the enclosure/PCB outline for the rail clip ecosystem early.

## 8. Hazardous Areas (ATEX/IECEx) Awareness

- If the product goes into explosive atmospheres (oil/gas/chemical/dust): Ex protection concepts (Ex i intrinsic safety — energy-limited circuits; Ex e, Ex m encapsulation) are certification territory with strict design rules (component derating, spacings, thermal limits, certified barriers).
- Intrinsic safety affects everything: max stored energy, component selection, PCB spacing, thermal design — it must be in the design from Gate 0. Retrofitting Ex is effectively a redesign. State clearly: Ex certification needs a notified body from day one.
