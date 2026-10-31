# Circuit and Schematic Design for Embedded Products

Designing, not just reviewing (hardware-review.md reviews; this file designs). Show the math for every component choice — an undocumented value is an unverified value.

## Contents
1. Design workflow and schematic discipline
2. Power supply design (the foundation)
3. Protection circuits
4. Reset, clock, and boot circuits
5. Analog front-end design
6. Filters
7. Component selection and derating
8. Digital interface circuits

---

## 1. Design Workflow and Schematic Discipline

- Block diagram first: power tree + signal tree, each block with voltage/current/interface — verify feasibility before placing a single symbol.
- Reference designs: start from vendor EVK schematics (MCU, radio, charger, sensor) — deviate only knowingly; deviations are where the bugs live.
- Schematic rules: hierarchical sheets by function; power symbols consistent; every net that leaves the board named; test points on every rail and critical signal; comments on the sheet for non-obvious values ("100 Ω: rise-time damping for 50 MHz SPI").
- ERC clean, then design review against hardware-review.md — review your own schematic as if someone else designed it.

## 2. Power Supply Design (the Foundation)

**Architecture choice:**
| Topology | Use when | Watch-outs |
|---|---|---|
| LDO | ΔV small, current <500 mA, noise-sensitive analog/RF | Power dissipated = (Vin−Vout)×I — compute junction temp |
| Buck | ΔV large or current high | Ripple/EMI near RF and ADC; inductor selection; layout is half the design |
| Boost/buck-boost | Battery range straddles Vout | Efficiency dip in transition region |
| Charge pump | Small currents, inductor-free | Ripple, limited current |

**Buck design math (show it):**
- Inductor: L = (Vin−Vout)·D/(ΔI·fsw), ΔI = 20–40% of Iout max; Isat ≥ Ipeak with 30% margin.
- Output cap: for ripple ΔV: C ≥ ΔI/(8·fsw·ΔV) plus transient step requirement; use the IC's recommended compensation — don't improvise loop compensation without measurement capability.
- Input cap: RMS ripple current rating matters, not just capacitance.
- Efficiency check at the actual load profile (light-load PFM mode for battery devices).

**LDO check:** P = (Vin−Vout)·Iload; θJA from datasheet → junction rise. A 5→3.3 V LDO at 300 mA dissipates 0.51 W — SOT-23 cannot, SOT-223 can. Show it.

**Radio peak currents:** supply sized for TX bursts (see hardware-review.md §1); bulk capacitance calculation: C ≥ I·Δt/ΔV (e.g., 400 mA × 5 ms burst with 100 mV droop → 200 µF).

## 3. Protection Circuits

- Input: reverse-polarity (P-MOSFET ideal-diode, not a series diode that drops 0.6 V), fuse/PTC for fault current, TVS for surges on external power.
- Every external connector pin: TVS to ground, series R (22–100 Ω) on signals; ESD guns find unprotected pins.
- Hot-swap on pluggable power: inrush limiter or hot-swap controller for larger systems.
- Battery: PCM/protection IC mandatory for Li-ion; NTC to charger (no charging <0 °C).
- Crowbar/OVP where overvoltage destroys the load.

## 4. Reset, Clock, and Boot Circuits

- Supervisor IC (not just RC) for anything with flash writes or motor loads: holds reset until VDD stable, asserts on brown-out, provides manual-reset input and watchdog input in one chip (e.g., TPS3823, STM809).
- RC reset acceptable only for benign loads — say why.
- Crystal: CL matching with C1=C2=2(CL−Cstray), Cstray≈3–5 pF — show the calculation; guard ring; no vias/signals under crystal; 32.768 kHz for RTC.
- Boot-strap pins: pulled with real resistors to production state (never floating); verify nothing external drives them during boot (see hardware-review.md §2).

## 5. Analog Front-End Design

- Sensor → ADC chain design, in order: source impedance → buffering (op-amp follower if >ADC limit) → RC anti-alias (fc ≈ fsample/10.../2, C ≥ 10× ADC sample cap) → range mapping (divider/offset so signal uses ≥80% of ADC span).
- Op-amp selection: input common-mode range includes signal; output swing to rail near 0 V; GBW ≥ 100× signal bandwidth; input bias current × source R < resolution budget.
- Reference: ratiometric sensors share excitation with ADC reference; absolute measurement needs a real reference (not noisy VDD) — compute error budget: reference % + ADC INL + resistor tolerance + tempco, summed worst-case or RSS.
- High-side vs. low-side current sense: high-side (INA199/INA219) preserves ground integrity; low-side is cheaper but lifts ground — decide explicitly.
- Bridge sensors (load cell): differential instrumentation path (HX711/INA or in-amp), excitation stability dominates accuracy.
- Guard against the classic: ADC input driven before MCU powered → back-powering through ESD diodes. Series R limits it; better: sequence power or use fail-safe buffers.

## 6. Filters

- RC low-pass: fc = 1/(2πRC) — pick R first (source impedance, noise: lower R = lower noise, more load), then C.
- Anti-alias: fc between highest signal frequency and fs/2; a 1st-order RC gives only −20 dB/decade — state whether that's enough attenuation at fs/2; if not, oversample harder or add a pole.
- Power-rail filtering: ferrite + caps (π filter) for analog/RF rails; verify ferrite's impedance peak at the noise frequency; watch LC resonance peaking — damp with R or cap ESR.
- Software and hardware filters are one design: hardware removes what aliases, software removes what doesn't (sensors.md §3).

## 7. Component Selection and Derating

- Resistors: 1% standard; 0.1% + low tempco where it sets accuracy; power derating 50% (a 0603 at its 100 mW rating runs hot).
- Capacitors: MLCC DC-bias derating is brutal — a 10 µF/0805/16 V X7R can be 3 µF at 5 V bias; check manufacturer curves, choose higher voltage rating or larger case. Electrolytics: lifetime halves per 10 °C — compute from ripple current and ambient.
- Inductors: Isat with margin, DCR for efficiency, shielded near RF.
- MOSFETs: Vgs(th) is NOT the drive spec — use RDS(on) at your gate voltage; gate charge for switching loss; SOA for linear/hot-swap use.
- Temperature grade: industrial (−40…+85 °C) minimum for products; automotive (−40…+125) where required; every electrolytic/aluminum part gets lifetime math.
- Derating rule of thumb: voltage ≤70% of rating, current ≤70%, power ≤50% — across the BOM, documented.

## 8. Digital Interface Circuits

- Level shifting: open-drain MOSFET shifter (BSS138) for I2C/low-speed; direction-aware or dedicated ICs (TXS/TXB) for push-pull medium speed; proper unidirectional buffers for SPI/high speed. Never rely on "5 V tolerant" without the datasheet saying it.
- RS-485/CAN: transceiver + termination (120 Ω ends) + bias resistors + common-mode choke for long runs + TVS array; isolated transceivers when ground potentials differ (industrial).
- USB: ESD array on D+/D−, 22 Ω series, shield grounding strategy stated.
- SD card: 50–100 mA switchable rail (power-cycle recovery), pull-ups per spec, short traces.
- Every connector: pin-1 marked, mechanical keying where possible, pinout chosen so a reversed mating can't apply power to signals (power/ground at symmetric positions).
