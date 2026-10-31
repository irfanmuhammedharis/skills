# embedded-firmware-engineering — Reference Bundle

This file bundles several reference documents into one, separated by clear headers, so they fit ChatGPT's knowledge file-count limit per Custom GPT / Project.

---



## FILE: references/actuators-power-hmi.md

# Actuators, Motors, Battery Power, and HMI

## Contents
1. Relays and solenoids
2. DC/stepper/BLDC motors
3. Battery charging and fuel gauges
4. Power path and ship mode
5. Displays
6. LEDs, buzzers, buttons — the HMI basics

---

## 1. Relays and Solenoids

- Drive circuit: transistor/MOSFET + flyback diode across coil (mandatory); contact side: RC snubber or TVS for inductive AC loads; inrush rating for capacitive loads (LED drivers, motors).
- Safe state: relay driver must default OFF at MCU reset — pull-down on the gate; the FMEA S≥4 rule: consider a watchdog-controlled enable (output needs periodic refresh) for hazardous loads.
- Contact wear: derate to ≤60% of rated current for inductive loads; minimum switching current matters for signal relays (wetting) — gold-clad contacts for mA signals.
- Firmware: debounce relay commands, enforce min on/off times (compressor anti-short-cycle), count operations for maintenance.

## 2. DC / Stepper / BLDC Motors

- Brushed DC: H-bridge with dead-time, current sense (cycle-by-cycle limit), back-EMF considerations, PWM frequency above audible (>20 kHz) if noise matters — verify driver IC supports it.
- Stepper: step/dir drivers (A4988, TMC2209 — TMC for silent + StallGuard sensorless homing); acceleration ramping in firmware (trapezoid/S-curve) or stalls; never lose steps silently in a precision product — encoder feedback or StallGuard validation.
- BLDC: use a controller (ESC, or FOC via STM32 MC SDK / VESC-style firmware) — don't hand-roll FOC unless that's the product.
- Common firmware requirements: current/temperature monitoring, stall detection (current spike or no encoder motion), controlled stop vs. coast defined, and a hard ESTOP path that does not depend on software.

## 3. Battery Charging and Fuel Gauges

- Charger ICs: TP4056 (cheap, no power path — battery powers load while charging: verify thermal and termination behavior under load), MCP73831, BQ2407x (power path), BQ2589x (I2C, high current). For products: power-path chargers so the system runs from adapter with battery absent/full.
- Charge parameters are set by resistor/I2C config — verify against battery datasheet (charge current ≤0.5C typical, termination, temperature window: Li-ion must not charge below 0 °C — NTC on battery pack wired to charger).
- Protection: pack-level PCM + firmware undervoltage cutoff; a deeply discharged Li-ion must be pre-charged at low current — good charger ICs handle this; verify.
- Fuel gauges: BQ27441/MAX17048 (I2C, learn battery profile) beat voltage-divider estimation badly — voltage-vs-SoC is nearly flat mid-range for Li-ion. If using ADC estimation, document ±10–15% error and never use it for safety decisions.
- Firmware: SoC reporting, low-battery graceful degradation (reduce TX power/rate), critical-battery safe shutdown with state saved, charge-state telemetry.

## 4. Power Path and Ship Mode

- Ship/storage mode: device must drop to <5 µA (or full cutoff) for shelf life — a device that arrives with a dead battery is DOA. Implement: long-press wake, or first-charge activation.
- Load switches on peripheral rails (sensor power, radio) let firmware kill hung hardware — the recovery primitive (see hardware-review.md §1).
- Supercaps: where power-loss warning time is needed (save state, send last gasp message), size for the energy of that sequence + margin; test the actual hold-up time.

## 5. Displays

- OLED (SSD1306/SH1106, I2C/SPI): full-buffer redraw is slow over I2C — use partial updates; burn-in for static content; contrast/lifetime derating.
- TFT (ILI9341/ST7789, SPI): SPI at 40–80 MHz needs short traces; use DMA double-buffering; LVGL for UI — frame buffer RAM budget dominates (partial buffers for small MCUs).
- E-paper: partial vs. full refresh rules, temperature-dependent waveforms, deep sleep between updates (that's the point); never leave it mid-refresh on power loss (ghosting/damage) — capacitor for refresh completion or accept cosmetic risk.
- Segment LCD: HT1621-style drivers or MCU LCD controller; ultra-low power — the right choice for battery devices.
- Common: define display behavior during faults and OTA (don't freeze stale "OK" status — the FMEA "wrong data" failure mode applies to UI too); backlight auto-dim; watchdog-refresh the UI so a hung device shows something visibly wrong.

## 6. LEDs, Buzzers, Buttons — HMI Basics

- LEDs: current-limit per color forward voltage; PWM dimming; define a system-wide indication language (colors/blink patterns for states and faults) and document it — users and factory both depend on it.
- Buzzer: passive buzzers need PWM; drive via transistor; never block on melody playback (non-blocking tone sequencer).
- Buttons: hardware debounce (RC) or firmware debounce (10–30 ms, state-machine based, not delay); define short/long/very-long press semantics; a wake-from-sleep button needs the right pin (RTC/NMI-capable).
- Enclosure reality check: LED light pipes, button feel, display viewing angle — firmware gets blamed for bad industrial design; flag issues early.


---


## FILE: references/antenna-rf.md

# Antenna and RF Design for Embedded Devices

## Contents
1. Antenna selection by radio
2. Matching networks
3. PCB layout rules
4. Link budget calculation
5. Coexistence and EMI
6. Regulatory basics
7. Validation and test

---

## 1. Antenna Selection by Radio

| Radio | Typical antennas | Notes |
|---|---|---|
| BLE / Wi-Fi / Zigbee (2.4 GHz) | PCB inverted-F / meander, chip antenna, external whip/U.FL | PCB antenna cheapest; chip antenna easiest but needs keep-out; external best performance |
| Sub-GHz (433/868/915 MHz) | Helical, whip, PCB loop | Quarter-wave whip at 868 MHz ≈ 82 mm — size often forces external |
| LoRa | Same as sub-GHz | Efficiency dominates range more than TX power |
| GNSS | Active ceramic patch, helix | Needs LNA supply (3.3/5 V bias-tee); ground plane size affects gain strongly |
| Cellular LTE-M/NB-IoT | Flex PCB, external monopole | Wide band (700–2200 MHz) — use vendor-certified antenna; carrier certification may mandate specific antennas |
| 60 GHz radar | Integrated AiP | Do not place metal within the radar FOV; radome material must be RF-transparent |

Selection order: check if the module has an integrated certified antenna (easiest regulatory path) → external connector (best performance, enclosure-dependent) → chip antenna → custom PCB antenna (needs VNA tuning; only with RF capability on the team).

## 2. Matching Networks

- Always place a π-network (series + two shunt pads) between radio and antenna, even if you populate it as 0 Ω + DNP. Untuned designs are unfixable without a board spin.
- Target: |S11| < −10 dB across the operating band (better than −6 dB absolute minimum), measured with a VNA on the final enclosure+PCB assembly.
- Matching changes with enclosure, battery, nearby metal, and hand/body proximity — measure in the final mechanical configuration.
- Keep the RF trace 50 Ω controlled impedance: compute width from stackup (state dielectric, height, Er); keep it short, no vias if possible, solid ground beneath.

## 3. PCB Layout Rules

- Follow the module vendor's reference layout exactly for the RF section — deviation voids modular certification assumptions.
- Ground plane: uninterrupted under the RF path and module; via stitching around the RF trace edges.
- Antenna keep-out: no copper (any layer) under/around PCB or chip antennas per datasheet; no metal (battery, shielding, displays) within the keep-out; plastic enclosure ≥ a few mm away.
- Crystals: short symmetric traces, guard ground ring, no signals crossing beneath.
- Decoupling at the radio: bulk cap sized for TX current pulses near the radio power pins; RF PA supply routed wide and short.
- Never route high-speed digital (SDIO, USB, display clocks, switching regulators) near the antenna; switching regulator harmonics at the radio band = desense. Use shielded inductors and spread-spectrum if available.

## 4. Link Budget Calculation

Show this math for every wireless design:

```
RX power (dBm) = TX power + TX antenna gain − path loss + RX antenna gain − margin
Path loss (free space, dB) = 20·log10(d_km) + 20·log10(f_MHz) + 32.44
```

- Compare RX power vs. receiver sensitivity (datasheet, at the actual data rate/SF); require ≥10 dB link margin for indoor/urban, ≥20 dB where reliability matters.
- Indoor: add 10–30 dB per wall depending on material; body loss near 2.4 GHz wearables: 10–20 dB.
- Example: BLE at 0 dBm TX, −95 dBm sensitivity, free-space budget 95 dB → ~1 km line-of-sight, but indoors assume 3–6 dB/10 m path exponent → realistic 10–30 m. State assumptions.

## 5. Coexistence and EMI

- Wi-Fi + BLE same chip: time-division on shared antenna — expect BLE throughput drops during Wi-Fi TX.
- GNSS + cellular: cellular TX harmonics desensitize GNSS — filter/isolate, and test GPS lock during data transmission.
- Radar (60 GHz) + 2.4 GHz: no direct interference, but radar MCU clock harmonics can leak — shielding review.
- Switching regulators: choose frequencies whose harmonics avoid the RX band; verify with near-field probe or at minimum conducted measurement.

## 6. Regulatory Basics (Design Consequences, Not Legal Advice)

- Pre-certified modules (ESP32-WROOM, nRF52 modules, etc.): keep the reference layout and antenna type — then only intentional-radiator requirements are largely inherited; change the antenna and you may need re-certification.
- ISM band rules differ: FCC 915 MHz (US, frequency hopping or DSSS, higher power OK), ETSI 868 MHz (EU, duty-cycle 0.1–10% per sub-band), 2.4 GHz worldwide but power/EIRP limits differ.
- Duty-cycle enforcement is firmware's responsibility on LoRa/sub-GHz in EU — implement airtime accounting.
- SAR evaluation may apply for body-worn >20 mW devices.
- Plan pre-compliance testing (radiated emissions + spurious) before formal certification; fixes are 10× cheaper pre-cert.

## 7. Validation and Test

- Minimum RF validation without a lab: RSSI sweep at known distances/orientations vs. a reference device; packet-error-rate test at margin boundary (≤1% PER target at deployment distance); test inside final enclosure.
- With a VNA: verify S11 across band in final assembly.
- With a spectrum analyzer: check TX power, harmonics, spurious vs. regulatory mask.
- Over-the-air firmware behavior: verify the radio stack degrades gracefully at the edge of range (retries, buffering, no watchdog resets from stack stalls).


---


## FILE: references/arduino.md

# Arduino Platform (AVR, ARM, ESP cores) — Production Use

## Contents
1. Platform scope and limits
2. AVR (Uno/Nano/Mega) specifics
3. ARM cores (Due, Zero, MKR, Nano 33)
4. Writing reliable Arduino code
5. Moving from Arduino to production
6. Library vetting rules

---

## 1. Platform Scope and Limits

Arduino is a framework, not hardware: the same `setup()/loop()` API runs on AVR (Uno, Nano, Mega), SAMD (MKR, Zero), STM32 (via STM32duino core), ESP32/ESP8266 (via espressif cores), and nRF52 (via Adafruit/Seeed cores). Code portability across cores is partial — verify pin maps, ADC resolution, PWM frequency, and interrupt support per core.

Honest limits: Arduino core hides the clock tree, prioritizes ease over timing accuracy, and many libraries block. Acceptable for prototypes, education, and low-risk products; for anything with safety, power, or volume constraints, treat Arduino code as a prototype to be hardened (see §5).

## 2. AVR (ATmega328P/2560) Specifics

- Resources: 32 KB flash / 2 KB RAM (328P) — RAM exhaustion is the #1 failure. Check free RAM at runtime (`freeMemory()` pattern via stack/heap gap); keep ≥300 B headroom.
- Use `PROGMEM` and `F()` macro for all string literals — strings in RAM kill 328P projects silently.
- `millis()` wraps at ~49.7 days: always use subtraction-based comparisons (`if (millis() - last >= interval)`), never `millis() > deadline`.
- `delay()` blocks everything — replace with non-blocking state machines for anything beyond trivial sketches.
- Serial: `HardwareSerial` buffers are 64 B — bursts beyond that drop bytes silently. Drain or enlarge.
- EEPROM: ~100k write cycles; use wear-leveling or write-on-change; AVR EEPROM writes can corrupt mid-write on brown-out — enable BOD fuse (4.3 V for 5 V boards).
- Watchdog: enable via `wdt_enable()`; the old optiboot/bootloader issue (endless reset on WDTO_15MS) is fixed in modern cores — verify on the actual board.
- PWM: default ~490 Hz (pins 5/6 ~980 Hz) — audible whine on motors/LEDs; change timer prescaler if it matters, documenting side effects (pins 5/6 affect millis via Timer0 — do not touch Timer0 prescaler).

## 3. ARM Cores (SAMD21, STM32duino, nRF52 cores)

- 3.3 V logic — not 5 V tolerant (SAMD); level-shift all 5 V peripherals.
- SAMD21: native USB — USB disconnect during `Serial.print` can block; guard with `if (Serial)`.
- STM32duino: exposes HAL underneath; you can mix Arduino API with direct HAL calls — document when you do.
- Adafruit nRF52 core: runs on SoftDevice — see nrf.md; `delay()` in this core yields to the BLE stack, but timing-critical bit-banging still breaks radio events.
- Interrupts: use `attachInterrupt(digitalPinToInterrupt(pin), ...)`; ISRs must be short — flag-and-return.

## 4. Writing Reliable Arduino Code

- Structure every non-trivial sketch as: pin/config constants → module objects (sensor, comms) with `begin()`/`update()` → super-loop calling non-blocking `update()` methods → watchdog refresh last.
- Avoid `String` class on AVR — heap fragmentation causes crashes after hours/days. Use fixed `char` buffers with `snprintf`.
- Every I2C/SPI sensor `begin()` return must be checked; fail into a defined error state with serial/LED diagnostic, never continue blind.
- Add a watchdog + reset-cause log even in Arduino projects (`wdt.h` on AVR, core-specific elsewhere).
- Pins: define with `constexpr uint8_t PIN_X = n;` at top; never scatter raw pin numbers.
- Time: `millis()`/`micros()` subtraction pattern only; on cores with tickless idle verify millis behavior during sleep.

## 5. Moving from Arduino to Production

Graduation path when the product gets serious:
1. Keep Arduino framework but move to PlatformIO (see toolchains-platformio.md): unit tests (`pio test` with Unity), CI builds, dependency pinning, `build_flags` per environment (debug/release).
2. Replace blocking library calls with non-blocking drivers; add proper error paths.
3. Port to native SDK when you hit: hard timing requirements, power targets Arduino sleep can't meet, memory ceilings, or certification requirements. Targets: ESP-IDF (ESP32), nRF Connect SDK (nRF52), STM32 HAL/LL (STM32), AVR bare metal or avr-libc.
4. Whatever survives: the pin map, state machines, protocol parsers, and test cases — port those, not the library calls.

## 6. Library Vetting Rules

Arduino libraries are the biggest quality risk. Before adopting any library:
- Check maintenance: last commit, open issues, forks. Abandoned library = own the code.
- Read the source for: blocking `while` loops without timeout, dynamic allocation patterns, ISR safety, `delay()` calls.
- Check the license (LGPL/static-linking implications for commercial products).
- Pin exact versions (`platformio.ini` or library manager JSON), never float "latest".
- Test the library's failure paths (sensor disconnected, NACK, garbage data) yourself — most libraries only demo the happy path.


---


## FILE: references/circuit-design.md

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


---


## FILE: references/communication-protocols.md

# Communication Protocols: Wired Buses and Wireless Stacks

## Contents
1. UART
2. I2C
3. SPI
4. CAN / Modbus
5. USB
6. BLE
7. Wi-Fi
8. LoRa / LoRaWAN
9. Zigbee / Thread / Cellular
10. Application-layer protocols (MQTT, CoAP, HTTP)

---

## 1. UART

- Baud accuracy: compute baud error % = (actual − target)/target; keep <2% total budget (both ends combined). Show the divider math.
- Always frame protocols: header/sync + length + payload + CRC16. Never parse raw streams byte-hunting without sync bytes.
- Handle: framing errors, overrun (ORE), noise flags — clear and count them; rising error counts = wiring/baud problem, log it.
- RX via ring buffer + DMA or ISR; never poll in a blocking loop in production code.
- RS-485: add DE/RE timing (settle before TX, hold after last stop bit), 120 Ω termination at both ends, bias resistors, and fail-safe for idle bus.

## 2. I2C

- Pull-up sizing: Rp(min) = (VDD − 0.4 V)/3 mA; Rp(max) = tr(max)/(0.8473 × Cb). For 400 kHz, tr ≤ 300 ns. Show the calculation with assumed bus capacitance.
- Every transfer checks ACK; NACK = retry with backoff, then bus-recovery (toggle SCL 9× until SDA releases), then re-init peripheral, then power-cycle device rail.
- Clock stretching: slave sensor may stretch — ensure master supports it.
- SMBus timeout: 25–35 ms total transfer watchdog — a hung I2C transaction must never hang the system.
- Address conflicts: scan at boot in debug; document all addresses in the ICD.

## 3. SPI

- Verify mode (0–3) and max clock per device; the slowest device on a shared bus does not limit others if each gets its own config at CS time.
- Shared MISO: confirm all slaves tri-state when CS high; if unsure, 1–10 kΩ series resistors or separate buses.
- Long traces (>15 cm) at >10 MHz: expect reflections — slow down or add series termination.
- DMA double-buffering for displays/ADC streams; handle CS framing across DMA transfers.

## 4. CAN / Modbus

- CAN: bit timing must be calculated (show quanta math), termination 120 Ω both ends; implement bus-off recovery (automatic re-init after controller recovery); filter IDs in hardware.
- Modbus RTU: 3.5-char inter-frame gap via timer; CRC16-Modbus on every frame; master timeout + retry policy; exception codes must be mapped to system errors, not ignored.
- Industrial deployments (CANopen, EtherCAT, PROFINET, EtherNet/IP, IO-Link, OPC UA, RS-485 network engineering): see [industrial-protocols.md](industrial-protocols.md).

## 5. USB

- CDC/ACM for debug is fine; for production devices define behavior when USB disconnects mid-transfer.
- USB suspend current matters for bus-powered devices — implement proper suspend/resume.

## 6. BLE

- Architecture: GATT services with 16-bit or custom 128-bit UUIDs; notify/indicate for streaming sensor data; write-with-response for config.
- Connection parameters: state them explicitly (interval, latency, timeout) — they dominate both latency and power.
- Security: use bonding + LE Secure Connections for anything beyond public sensor data; justify if open.
- MTU negotiation + data-length extension for throughput; chunk long writes.
- Handle disconnect reasons; implement supervision-timeout recovery and reconnection with backoff. nRF52: mind SoftDevice flash-write stalls.
- Throughput reality check: ~5–20 kb/s effective with default MTU at short intervals — do not promise raw radio rates.

## 7. Wi-Fi

- Credential provisioning: define it (AP mode, BLE-assisted, SmartConfig) — never hardcode.
- Reconnection state machine: connect → backoff (exponential, capped, with jitter) → fallback AP mode after N failures. Log every disconnect reason code.
- Power: DTIM sleep modes; radio TX current spikes (ESP32 ~350–500 mA) — decouple accordingly.
- Coexistence with BLE on shared radios: expect latency jitter; do not run hard real-time tasks on the same core during TX bursts.

## 8. LoRa / LoRaWAN

- Link budget first: SF vs. range vs. airtime tradeoff; show the calculation before claiming range.
- Duty cycle limits (EU868: 1% default) — compute airtime per message and enforce in firmware.
- LoRaWAN: use a maintained stack (LoRaMac-node, Arduino-LMIC successors); ADR on for static devices, off/limited for mobile; confirmed uplinks sparingly; handle join failures with backoff, respect retransmission rules.
- Class A default; Class C only for mains-powered.
- Payload: keep ≤51 bytes at low DR; design compact binary payloads.

## 9. Zigbee / Thread / Cellular

- Zigbee/Thread: use vendor stacks (Zigbee2MQTT compatibility for consumer); network formation/join failure recovery; sleepy end-device polling interval defines latency and battery life.
- Cellular (LTE-M/NB-IoT): modem AT-command state machine with timeouts on every command; handle network registration loss gracefully; PSM/eDRX configuration; SIM failure detection. Plan for ~100 mA average during TX bursts and multi-second attach times.
- GNSS modules: NMEA parsing with checksum validation; TTFF budgets; antenna supply short detection.

## 10. Application-Layer Protocols

- **MQTT**: QoS0 for telemetry streams, QoS1 for commands/events that must arrive; Last Will for presence; clean session vs. persistent session decided explicitly; TLS mandatory for WAN; client ID + topics namespaced per device.
- Reconnect with exponential backoff + jitter; buffer critical messages in flash (with wear consideration) during outages; document max outage the buffer covers.
- **CoAP**: for constrained/UDP networks; confirmable messages for critical data; observe for streams.
- **HTTP(S)**: acceptable for provisioning/OTA; too heavy for frequent telemetry on constrained links.
- **Payload format**: binary (CBOR/Protobuf/custom packed struct with version byte) for constrained links; JSON only where bandwidth is cheap and debuggability wins. Every payload format gets a version field from day one.


---


## FILE: references/debugging-methodology.md

# Systematic Debugging Methodology for Embedded Systems

## Contents
1. The disciplined process
2. Bug class playbook
3. Race conditions and Heisenbugs
4. Post-mortem from reset/fault data
5. Field returns and fleet debugging
6. Instrumentation that doesn't change behavior

---

## 1. The Disciplined Process

1. **Reproduce deterministically first.** Write down exact steps/conditions/stimulus. A bug you can't reproduce is a bug you can't verify fixed. If intermittent: build a harness that triggers it automatically (loop the operation, log until failure).
2. **Stabilize the observation.** Get visibility before changing anything: logs, scope, debugger. One reliable observation beats ten theories.
3. **Bisect the space.** Hardware vs. software (swap board), code vs. config (revert build), when-introduced (git bisect across commits), which subsystem (disable half). Each experiment must halve the remaining space.
4. **One variable at a time.** Change one thing, observe, record. Shotgun changes create fixes you don't understand — which return.
5. **Prove the fix.** Re-run the reproduction harness N× the failure frequency (failed 1/hour → run 24 h clean minimum), then add a regression test so it can never come back silently.
6. **Write the post-mortem**: symptom → root cause → fix → prevention. Root cause means "why did the process let this through," not just the line of code.

## 2. Bug Class Playbook

| Symptom | Most likely causes (check in order) |
|---|---|
| Random resets | Watchdog (which task starved?) → brown-out (scope the rail during radio TX) → stack overflow (watermarks) → hard fault (read CFSR/BFAR) |
| Works on bench, fails in field | Temperature (crystal drift, battery voltage drop) → power quality → RF environment → uninitialized state only exercised by field sequence |
| Dead after days/weeks | Counter rollover (millis 49.7 d, tick wrap) → memory leak/fragmentation → flash wear → resource leak (sockets, mutexes) → RTC drift |
| Hangs at boot sometimes | Power sequencing/ramp → crystal startup margin → peripheral left running by bootloader → race between init order |
| Data corrupts rarely | ISR/task shared data without protection → DMA + cache coherency (M7) → buffer overrun → flash write during operation |
| I2C/SPI device stops responding | Bus lockup (recovery sequence?) → sensor brown-out (switchable rail?) → NACK storm after ESD |
| Works with debugger attached, fails standalone | Timing dependency (semihosting delay) → uninitialized variable (debug zeroes memory) → watchdog disabled in debug builds |

## 3. Race Conditions and Heisenbugs

- Detection: they move when you add logging. Counter-instrument instead: count events, queue depths, ISR/task interleavings; dump counters periodically — logging changes timing, counters barely do.
- Reproduce by stress: maximize preemption (high-rate timers, artificial load tasks, loopback traffic at max rate); races appear under load, not on the bench.
- Audit pattern: list every shared variable; for each, identify writers and readers (task/ISR context); verify protection. Grep for `volatile`, every one must justify itself.
- Common races: ISR sets flag, task clears after processing but ISR fires between (use atomic swap/queue); multi-byte value torn by ISR mid-read (critical section or atomic snapshot); check-then-act on shared state.
- Priority inversion symptoms: high-priority task occasionally misses deadline while a low-priority task runs — check mutex usage (see real-time-analysis.md §5).

## 4. Post-Mortem from Reset/Fault Data

Mandatory infrastructure (build it before you need it):
- Reset-cause register read + persisted at boot.
- HardFault handler capturing: stacked PC/LR/xPSR, CFSR/HFSR/BFAR/MMAR (Cortex-M), task name, heap/stack watermarks — stored to flash or no-init RAM, retrievable via debug UART and uploaded to cloud.
- Decode: BFAR valid → bus fault at that address (often null/wild pointer); usage fault UNDEFINSTR → corrupted PC (stack smash); IMPRECISERR → enable write-buffer disable or narrow by disabling instructions until precise.
- Keep a ring buffer of last N events (boots, faults, assert codes, resets) in retained RAM — the "black box" that survives the crash.

## 5. Field Returns and Fleet Debugging

- Every field unit must be diagnosable without opening it: version, uptime, reset count by cause, fault counters, last crash dump — queryable over its normal comms channel.
- Fleet telemetry: track reset rate per firmware version per cohort — a 0.5%/day reset rate is invisible on the bench and catastrophic at 10k units.
- Returned units: never reflash before extracting the black-box data and config — the evidence is the product of the return.
- Correlate with environment: batch/date codes, temperature, supply, installation site — field failures cluster by conditions, not randomly.

## 6. Instrumentation That Doesn't Change Behavior

- Prefer: GPIO pulse + logic analyzer (sub-µs cost), DWT cycle counters, event counters, RTT (J-Link, fast and buffered) over UART printf (slow, blocking, changes timing).
- Trace tools: Segger SystemView (RTOS event timeline), Percepio Tracealyzer — see actual task/ISR scheduling vs. intended design.
- Compile-time instrumentation levels: keep the hooks in production (compiled out by level), so the same binary can be diagnosed.
- Golden rule: if the bug vanishes with instrumentation, the instrumentation is the variable — switch to lower-impact observation, don't declare victory.


---


## FILE: references/embedded-c.md

# Embedded C: Production Language Discipline

## Contents
1. Type and arithmetic discipline
2. volatile, atomics, and shared data
3. Register and bit manipulation patterns
4. Fixed-point math
5. Memory: sections, linker, startup
6. Driver architecture in C
7. Undefined behavior traps
8. Host-based unit testing of C

---

## 1. Type and Arithmetic Discipline

- Always fixed-width: `uint8_t/uint16_t/uint32_t/int32_t` from `<stdint.h>`; `int` is forbidden in portable driver code (width varies).
- Signedness: unsigned for registers/protocols/bitfields; signed only when negatives are real. Never compare signed against unsigned (`-Wsign-compare` must be on).
- Overflow is design input: for every counter, state the wrap time (32-bit ms tick wraps at 49.7 days — handle with subtraction arithmetic: `(int32_t)(now - deadline) >= 0`).
- `size_t` for sizes/indices; `ptrdiff_t` for pointer arithmetic; cast deliberately, never implicitly narrow.
- Avoid float on MCUs without FPU (10–100× slower, pulls in big libraries). If FPU exists, verify ISR context saving cost before using float in interrupts.

## 2. volatile, atomics, and Shared Data

- `volatile` means "this can change outside the compiler's view" — required for: ISR-shared variables, MMIO registers, variables touched by DMA buffers. It is NOT a synchronization primitive.
- Shared-data rules:
  - Single-byte flag ISR→task: `volatile` + clear-after-read is acceptable.
  - Multi-byte data ISR→task: critical section (disable IRQ / RTOS taskENTER_CRITICAL) around read, or lock-free single-writer circular buffer.
  - Multi-producer: use an RTOS queue — hand-rolled multi-producer lock-free code is a PhD thesis, don't.
- Compiler barriers: `__DMB()`/memory clobber when ordering matters (DMA descriptor setup before enabling DMA).
- Audit pattern: grep `volatile` — every instance must have a comment naming its writer contexts.

## 3. Register and Bit Manipulation Patterns

- Read-modify-write with masks; never magic numbers:
```c
#define ADC_CR1_RES_Pos      (24U)
#define ADC_CR1_RES_Msk      (0x3U << ADC_CR1_RES_Pos)
reg = (reg & ~ADC_CR1_RES_Msk) | (0x2U << ADC_CR1_RES_Pos);
```
- CMSIS headers on Cortex-M — use vendor SVD-derived headers, not hand-written addresses.
- Struct overlays on registers: legal only with exact packing + volatile members; prefer CMSIS-style definitions.
- Bit-banding/bit-fields: avoid for portable code; avoid C bit-fields for hardware registers (layout is implementation-defined — the standard trap).
- Every register write in driver init: comment with datasheet reference ("RM0390 §13.4.2: enable dual regular simultaneous mode").

## 4. Fixed-Point Math

- Represent quantities in scaled integers: millivolts, centi-degrees, Q15/Q31 for DSP. Document the scale at the type: `typedef int32_t millivolt_t;`
- Q-format arithmetic: Q15 multiply = `(a*b)>>15` with int32 intermediate; watch overflow — saturate deliberately (`__SSAT` on Cortex-M or explicit clamp).
- Division: precompute reciprocals as shifts where the divisor is constant; avoid 64-bit division on M0 (pulls big library).
- Filters in fixed point: state and coefficients in wider type; verify no overflow at worst-case input (show the analysis).

## 5. Memory: Sections, Linker, Startup

- Know your linker script: `.text .rodata .data .bss .stack .heap`, plus custom: `.noinit` (survives reset — black-box data), `.ccmram`, `.ramfunc` (code from RAM for flash-write-time execution).
- Startup code: vector table → copy .data flash→RAM → zero .bss → call static constructors (C++) → main. Bootloader-left state must be de-initialized before this (clocks, DMA, interrupts).
- No-init section usage pattern: magic word + CRC validates contents after watchdog reset; discard on cold boot.
- Stack: single main stack + ISR stack model vs. per-task RTOS stacks; size from measurement (reliability-testing.md), guard via MPU or fill-pattern check.
- Heap policy: none in long-running devices (fragmentation is a slow DoS); static pools with block sizes per use case when needed; `malloc` in init-only paths is acceptable with justification.

## 6. Driver Architecture in C

- One module = one `drv_xxx.c/h`; header exposes only opaque handle + init/config/process API; state in a struct, not globals (multi-instance ready).
- Layering enforced by include discipline: application includes driver headers; drivers never include application headers.
- Every driver: `init()` returns status, `deinit()` for power management, `self_test()` where hardware supports it, error enum shared project-wide.
- Non-blocking pattern: `start()` → interrupt/DMA → callback/flag → `result()`. Blocking variants exist only as wrappers with timeout for init-time use.
- Config via struct passed to init (baud, pins abstracted as instance data) — no `#define`-configured drivers in reusable code.
- Defensive ABI: validate pointers/ranges at API boundary, not at every internal call.

## 7. Undefined Behavior Traps

- Shift by ≥ width or negative: UB — mask and range-check shift amounts.
- Signed integer overflow: UB (not wrap!) — use unsigned for wrap-around semantics.
- Strict aliasing: no type-punning through pointers (use `memcpy` or unions); compile `-fno-strict-aliasing` if legacy code demands it — document why.
- Uninitialized reads, out-of-bounds, use-after-free: enabled sanitizers in host tests (ASan/UBSan) catch these before hardware does.
- `assert()` compiled out in release: never put side effects in assert expressions.

## 8. Host-Based Unit Testing of C

- Architecture payoff: pure logic (parsers, filters, state machines, CRC, schedulers) compiles for the host — hardware access behind a HAL interface mocked in tests.
- Framework: Unity/CMock or CppUTest; run with `gcc -fsanitize=address,undefined -Wall -Wextra -Werror`.
- State machines: transition-table tests (every state × every event including illegal).
- Parsers: fuzz lightly — random + mutated inputs for ≥10⁵ iterations under ASan/UBSan.
- This is the CI layer from toolchains-platformio.md §5; a firmware project without host tests is a prototype.


---


## FILE: references/esp32.md

# ESP32 Family (ESP32, S2, S3, C3, C6) — ESP-IDF and Arduino Core

## Contents
1. Variant selection
2. ESP-IDF architecture essentials
3. Critical gotchas (the flaws that bite)
4. Wi-Fi + BLE production patterns
5. OTA and partitions
6. Power management
7. Arduino-core-on-ESP32 notes

---

## 1. Variant Selection

| Variant | Core | Radio | Use when |
|---|---|---|---|
| ESP32 (classic) | Dual Xtensa LX6 | Wi-Fi + BT Classic + BLE | Legacy, BT Classic needed |
| ESP32-S3 | Dual Xtensa LX7 | Wi-Fi + BLE 5 | Default for new Wi-Fi designs; USB OTG, AI vector instructions, more GPIO |
| ESP32-C3 | Single RISC-V | Wi-Fi + BLE 5 | Cost-sensitive, simpler |
| ESP32-C6 | RISC-V | Wi-Fi 6 + BLE 5 + 802.15.4 | Thread/Zigbee + Wi-Fi combos |
| ESP32-S2 | Single Xtensa | Wi-Fi only | USB needed, no BLE |
| ESP32-H2 | RISC-V | BLE + 802.15.4 | Thread/Zigbee only, no Wi-Fi |

Check module vs. chip: use pre-certified modules (WROOM/WROVER/C3-MINI) unless volume justifies chip-down + certification. PSRAM (WROVER, S3-N8R8) only if the application needs it — PSRAM adds latency and power.

## 2. ESP-IDF Architecture Essentials

- ESP-IDF = FreeRTOS + lwIP + Bluetooth stack + drivers, component-based build on CMake. Pin the IDF version per project (`idf.py --version` documented; use release branches, not master).
- Task model: app tasks + system tasks (wifi, bt, lwIP, idle per core). Pin CPU-heavy tasks to a specific core (`xTaskCreatePinnedToCore`); Wi-Fi/BLE stack tasks run on core 0 by default — put real-time work on core 1.
- Interrupt allocation: use `esp_intr_alloc` flags correctly; IRAM-safe ISRs (`IRAM_ATTR`) required if the handler must run during flash operations — a non-IRAM ISR during flash write/erase crashes the chip.
- Logging: `ESP_LOGx` with per-tag levels; set production log level explicitly; route crash logs to flash for field retrieval (core dump partition or esp-coredump to UART).
- `sdkconfig`: treat as source — commit it, diff it between builds, document every non-default setting.

## 3. Critical Gotchas (the flaws that bite)

- **Brown-out on TX**: Wi-Fi TX bursts draw 350–500 mA; insufficient bulk capacitance or weak PSU → brown-out resets that look random. Add ≥10 µF + 100 nF near the module, use a PSU rated ≥1 A peak; keep the brown-out detector enabled (never disable it to "fix" resets — fix the power).
- **Flash wear + power-loss**: NVS is wear-leveled but not transactional against all power cuts; for critical config use NVS with versioned keys + validation, or littlefs/FATFS with power-fail-safe write patterns. Test by power-cycling during writes.
- **Strapping pins**: GPIO0/2/5/12(MTDI)/15(MTDO) on classic (S3/C3 differ) affect boot mode — using them for external circuits without checking boot strapping causes boards that don't boot. Always consult the strapping pin table before pin assignment.
- **ADC2 unusable during Wi-Fi** (classic ESP32): ADC2 conflicts with Wi-Fi radio. Use ADC1 channels, or an external ADC, when Wi-Fi is active.
- **ADC nonlinearity**: ESP32 ADC needs `esp_adc_cal` characterization; raw counts are notably nonlinear at the rails — use the calibration API and state achieved accuracy.
- **Cache-disabled panic**: any code/data in flash is inaccessible during flash erase/write — keep flash operations out of high-rate paths; use `IRAM_ATTR` for anything that must run concurrently.
- **GPIO matrix vs. IO_MUX**: high-speed signals (SPI >40 MHz, RMT, I2S) must use IO_MUX pins, not the GPIO matrix.
- **Stack sizes**: default Arduino/IDF task stacks overflow with printf-heavy code — measure with `uxTaskGetStackHighWaterMark`, enable `CONFIG_FREERTOS_CHECK_STACKOVERFLOW`.

## 4. Wi-Fi + BLE Production Patterns

- Wi-Fi event handling: use the event loop (`esp_event`), never poll status. Reconnect policy: exponential backoff (start 1 s, cap 5 min, ±20% jitter), and after N failures escalate (restart Wi-Fi driver → restart system → fall back to provisioning mode).
- Store credentials in NVS via a provisioning component (`wifi_provisioning` with BLE or SoftAP transport + proof-of-possession); never hardcode.
- BLE: choose Bluedroid (full-featured) or NimBLE (lighter, recommended for new designs); configure coexistence (`CONFIG_SW_COEXIST_ENABLE`) when Wi-Fi+BLE run together — expect BLE latency spikes during Wi-Fi TX; verify BLE notify throughput under Wi-Fi load.
- Watch the `wifi` task priority: starving it causes disconnects that look like network problems. Never block core 0.
- TLS: use `esp-tls` with CA bundle (`esp_crt_bundle_attach`); validate certificates — skipping verification on a WAN device is a fleet compromise waiting to happen.

## 5. OTA and Partitions

- Partition table: define explicitly (`partitions.csv`): factory/OTA_0/OTA_1 + nvs + phy_init + (optional) littlefs/coredump. Never use the default single-OTA layout for products.
- Use `esp_https_ota` with server cert validation; after update, the app must call `esp_ota_mark_app_valid_cancel_rollback()` only after self-tests pass (Wi-Fi connect, sensor check) — otherwise it auto-rolls-back on next boot. Test: kill power mid-download, mid-verify, mid-first-boot.
- Enable flash encryption + secure boot v2 for production (`idf.py` security features) — this changes the flashing workflow; document the production flashing procedure before enabling.
- Anti-rollback: `CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK` with secure version counter.

## 6. Power Management

- Modem sleep (DTIM) for connected-idle devices: ~10–20 mA average vs. ~80 mA without; light-sleep for wake-on-event; deep-sleep (~10 µA, ULP/RTC domain only) for battery devices.
- Deep-sleep state: only RTC memory persists (`RTC_DATA_ATTR`); design boot flow to distinguish cold boot vs. deep-sleep wake (`esp_sleep_get_wakeup_cause`) and skip re-init where valid.
- ULP coprocessor (RISC-V ULP on S3/C3) for sensor sampling during sleep — complex; justify against simply waking the main CPU.
- Measure: sleep current on the final board is often 10–100× datasheet due to devkit USB-UART chips, LDOs, and LEDs — measure on production hardware, not devkits.

## 7. Arduino-Core-on-ESP32 Notes

- Arduino core is a wrapper over ESP-IDF — you can call IDF APIs directly from Arduino sketches; do so for NVS, OTA, and power management rather than re-inventing.
- `loop()` runs as a task (core 1, priority 1); Wi-Fi runs on core 0 — long blocking code in `loop()` degrades but doesn't kill Wi-Fi; long blocking code in a high-priority task will.
- Use `Preferences` (NVS wrapper) not `EEPROM` emulation for new code.
- `esp_task_wdt` is enabled in recent cores — a `loop()` that never yields trips it; structure code non-blocking.


---


## FILE: references/firmware-security.md

# Firmware Security: Crypto, Keys, Secure Boot, and Threat Modeling

## Contents
1. Threat modeling (do this first)
2. Cryptographic primitives — what to use, what to avoid
3. Key storage and secure elements
4. Secure boot chain
5. OTA security
6. Debug and production lockdown
7. Common catastrophic mistakes

---

## 1. Threat Modeling (do this first)

- List assets: device identity/keys, user data, control authority (what can this device actuate?), fleet integrity, cloud credentials.
- List attackers: remote network attacker, local physical attacker (debug ports, flash extraction), supply-chain attacker (malicious update server, counterfeit parts), insider (factory credential leak).
- STRIDE the data flows: spoofing (auth), tampering (integrity), repudiation (logs), information disclosure (confidentiality), DoS (availability), elevation (authz).
- For each threat: countermeasure or documented acceptance. Output: a one-page threat model in the firmware spec — certification auditors and enterprise customers ask for it.
- Industrial/OT products: frame the work against **IEC 62443** (zones and conduits, security levels SL1–SL4, component requirements 62443-4-2, development process 62443-4-1) — industrial customers procure against it; map each countermeasure to its SL claims. Key 62443 consequences for firmware: no default credentials, role-based access, signed updates, audit logs, and network segmentation assumptions stated in the manual.

## 2. Cryptographic Primitives — What to Use, What to Avoid

- Use only vetted libraries: mbedTLS, libsodium (via Monocypher for tiny MCUs), TF-M/PSA Crypto on Cortex-M33, vendor crypto accelerators (ESP32, STM32U5, nRF with CryptoCell).
- Signing firmware: ECDSA-P-256 + SHA-256 (or Ed25519). Never RSA-1024, never homebrew MACs for image authentication.
- Transport: TLS 1.2+ with ECDHE ciphers; validate certificates (full chain + hostname + expiry); pin the CA, not a leaf cert (leaf rotates).
- Symmetric: AES-128-GCM/CCM. Never ECB. Never reuse nonces in GCM (catastrophic — use random 96-bit nonces or counters with reboot-safe persistence).
- Randomness: use the hardware TRNG; seeding software PRNG from time/ADC noise alone is a classic break. Verify TRNG is enabled and health-checked.
- Hash: SHA-256. Never MD5/SHA-1 for anything security-relevant.
- Password-derived keys: PBKDF2/scrypt with salt — never raw hash of password.
- Never implement crypto yourself. The correct amount of hand-rolled crypto in production firmware is zero.

## 3. Key Storage and Secure Elements

- Hierarchy (best→worst): secure element (ATECC608A/B, STSAFE, NXP SE05x — keys never leave the chip, crypto done inside) → MCU TrustZone/secure flash (STM32U5, nRF5340, ESP32 with flash encryption + eFuse keys) → obfuscated flash storage with readout protection (acceptable only for low-value assets).
- Per-device unique keys provisioned at manufacture — see iot-firmware.md §2. A shared fleet key converts one device teardown into total fleet compromise.
- ATECC608 integration notes: I2C, needs cryptoauthlib; provision in a controlled jig; lock the config zone AFTER provisioning (irreversible — test the flow on sacrificial units first).

## 4. Secure Boot Chain

- Chain of trust: ROM bootloader → verifies bootloader signature → bootloader verifies app → app runs. Each link verified with an immutable root key (eFuse/OTP).
- Enable on: ESP32 (Secure Boot V2 + flash encryption), STM32U5/H5 (SBSFU/TF-M), nRF (MCUboot + immutable bootloader, KMU key storage), RP2350 (signed boot). For parts without hardware root (F4, AVR), secure boot is software-only — document the limitation.
- Anti-rollback: monotonic security counter in eFuse/OTP; without it an attacker re-flashes an old firmware with known vulnerabilities.
- Debug the boot chain deliberately: unsigned image rejected (test it), tampered image rejected (flip a bit, test it), old-version image rejected (test it).

## 5. OTA Security

- Non-negotiables: signature verification before every boot + before install; TLS for transport; version monotonicity; rollback to last-known-good (availability is also security — a bricked fleet is a successful attack).
- Update server compromise is in scope: image signing keys live offline (HSM or air-gapped), NOT in CI secrets with broad access; transport TLS is not a substitute for image signatures.
- Broadcast updates: consider sequence counters vs. replay; a recorded valid update packet must not be replayable to downgrade.
- See microcontrollers.md §6 and platform files for mechanics.

## 6. Debug and Production Lockdown

- Production build: JTAG/SWD locked (RDP L1 STM32, APPROTECT nRF, eFuse ESP32, RP2350 debug disable); UART shell removed or behind per-device credential; no `printf` of keys/secrets at any log level.
- Provide an authorized service path: challenge-response unlock (J-Link/STM32 authenticated debug) or physical reflash by service — "locked forever" bricks returns analysis; "open" invites cloning. Choose deliberately, document it.
- RMA flow: how to extract black-box data from a locked device (see debugging-methodology.md §5) — solve this before locking the first production unit.

## 7. Common Catastrophic Mistakes

- Hardcoded credentials in firmware strings (extractable from a flash dump in minutes).
- TLS without certificate validation (`esp_wifi` demos and MQTT examples often skip it — never copy that pattern).
- Unsigned OTA ("we'll add it later" — later never comes before the incident).
- Shared fleet API keys, MQTT wildcard subscriptions allowing cross-device command injection.
- UART bootloader left enabled with erase/write commands in production.
- Predictable device IDs as the only authentication.
- Storing PII/secrets in crash dumps or logs shipped to the cloud.
- Side-channel awareness: for high-value targets, power analysis extracts keys from unprotected software AES — this is what secure elements and crypto accelerators with DPA resistance are for. Assess whether your threat model includes physical attack; if yes, software-only crypto on a plain MCU is insufficient.


---


## FILE: references/hardware-review.md

# Hardware/Schematic Review for Firmware Engineers

Review the schematic before writing firmware — half of "firmware bugs" are schematic bugs. This is the elite review checklist. For *designing* circuits from scratch, use [circuit-design.md](circuit-design.md) (power, protection, analog, component selection) and [pcb-layout.md](pcb-layout.md) (stackup, grounding, DFM).

## Contents
1. Power architecture review
2. Reset, boot, and clock circuits
3. Debug and programming access
4. Signal integrity and protection
5. Per-peripheral schematic traps
6. Firmware-relevant BOM checks

---

## 1. Power Architecture Review

- Regulator current headroom ≥2× worst-case MCU+radio peak (radio TX bursts, not averages). Check regulator transient response vs. TX current step — slow LDOs dip rail → brown-out.
- Decoupling present: 100 nF per MCU power pin, bulk (≥10 µF) near radio modules, per vendor reference design.
- Power sequencing: sensor/radio rails that need power-switching get a load switch with a GPIO — this is the firmware recovery mechanism for hung peripherals. No switchable rail = no power-cycle recovery.
- Battery: reverse-polarity protection, fuel gauge or at minimum ADC divider (mind divider leakage — use high-MΩ + switch or buffer), undervoltage cutoff before flash writes become unreliable.
- Verify every rail voltage vs. every connected IC's absolute max — 5 V into a 3.3 V pin kills slowly through ESD diodes.

## 2. Reset, Boot, and Clock Circuits

- Reset line: proper RC/supervisor, not just a pull-up; manual reset button reachable in the enclosure design.
- Boot-mode pins: pulled to production state, not floating; strap pins double-used as GPIO must be checked against external circuit driving them at boot (ESP32/S3 strapping, STM32 BOOT0, nRF reset/APP).
- Crystal: load capacitors matched to crystal CL (CL = (C1·C2)/(C1+C2) + Cstray — show the math); 32.768 kHz LSE present if RTC accuracy matters; TCXO only when spec demands.
- USB designs: 48 MHz clock accuracy path identified (HSE+PLL or dedicated), USBLC ESD + 22 Ω series + 1.5 kΩ pull-up control on FS.

## 3. Debug and Programming Access

- SWD/JTAG pads broken out and reachable on the production board (test points fine) — a board you can't debug is a board you can't fix.
- UART debug header with ground adjacent; label TX/RX **from the MCU's perspective** on silkscreen.
- Boot-mode selection accessible for recovery (jumper/test points).
- Don't let final enclosure/assembly make these unreachable — specify pogo-pin fixture points for production.

## 4. Signal Integrity and Protection

- Every external connector pin: ESD protection (TVS), and series R on signal lines leaving the board.
- Long cables (>10 cm) on GPIO/I2C: expect noise — RC filter or slew-rate control; I2C over cable needs lower speed and stronger pull strategy, ideally differential conversion (RS-485/CAN) instead.
- Analog inputs: RC anti-alias before ADC, source impedance within ADC spec, protection against overvoltage from sensor connector.
- High-current switching (relays/motors): flyback diodes (or TVS/RC snubber across AC loads), flyback return path doesn't share sensitive ground; star grounding or at minimum separated power/signal ground regions joined at one point.
- Level shifters wherever 5 V and 3.3 V domains meet (both directions).

## 5. Per-Peripheral Schematic Traps

- **I2C**: pull-ups present on the board (not assumed inside modules), value reasonable for bus capacitance/speed; addresses of all devices checked for conflicts.
- **SPI**: CS per device; MISO tri-state behavior verified for shared buses; series R placeholders on high-speed lines.
- **UART**: cross-wired TX/RX (the classic); flow-control pins if the protocol needs them; RS-485 transceiver DE/RE pins on controllable GPIOs with defined idle state.
- **CAN**: 120 Ω termination at bus ends (jumper-populated helps bring-up), transceiver standby pin controlled.
- **ADC reference**: clean reference (not raw VDD with switching noise) when accuracy matters; ratiometric sensors share the reference.
- **PWM/power outputs**: gate resistors on MOSFETs, pull-downs so outputs are OFF during MCU reset (boot pins float — the pull-down is the safe state).
- **Interrupt-capable sensors**: INT lines on interrupt-capable MCU pins, not random GPIO.
- **RF section**: matches module reference design exactly — see antenna-rf.md.

## 6. Firmware-Relevant BOM Checks

- MCU flash/RAM size with 2× headroom; temperature grade matches the product environment; package matches assembly capability.
- Second-source risk: single-source sensors/modules flagged; pin-compatible alternatives noted.
- Flash endurance of external flash/EEPROM vs. write frequency plan (see real-time-analysis.md §6).
- Every "NC" (not connected) pin per datasheet — some must be tied, not floated.
- Devkit-vs-product differences documented (devkit USB-UART draws mA, devkit LEDs, different crystals) — never validate power on a devkit.


---


## FILE: references/industrial-design.md

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


---


## FILE: references/industrial-protocols.md

# Industrial Communication Protocols

Factory-floor protocols are contract-driven, timing-strict, and certified. This file covers what communication-protocols.md doesn't: the industrial stack.

## Contents
1. Protocol selection map
2. Modbus RTU/TCP (the baseline)
3. RS-485 network engineering
4. CANopen / CAN in automation
5. Industrial Ethernet: EtherCAT, PROFINET, EtherNet/IP
6. IO-Link
7. OPC UA and MQTT Sparkplug (IT/OT boundary)
8. Time synchronization (PTP/NTP)

---

## 1. Protocol Selection Map

| Need | Protocol | Notes |
|---|---|---|
| Sensor/actuator to PLC, simple | Modbus RTU (RS-485) or 4–20 mA | Universal, slow, everywhere |
| Device-level, smart sensors | IO-Link | Point-to-point, diagnostics built in |
| Embedded network, machines/vehicles | CANopen / CAN (J1939 for vehicles) | Robust, prioritized, real-time |
| High-performance motion, daisy-chain | EtherCAT | Hard real-time, needs ESC hardware |
| PLC ecosystem integration | PROFINET (Siemens world), EtherNet/IP (Rockwell world) | Certification required |
| OT→IT data, SCADA/MES/cloud | OPC UA, MQTT Sparkplug B | The integration layer |
| Legacy instrumentation | HART over 4–20 mA | Analog + digital overlaid |

Pick by the customer's PLC ecosystem, not by preference. State which ecosystem the design targets at Gate 0.

## 2. Modbus RTU/TCP (the Baseline)

- RTU framing: 3.5-char silent interval as frame delimiter — implement with a hardware timer, not character counting; CRC16-Modbus (poly 0xA001, init 0xFFFF — `scripts/embedded_calc.py crc16 --refin` verifies).
- Function codes: support 03/06/16 minimum; exception responses (01/02/03/04) must be correct — masters log them.
- Register map is a public contract: document addresses, types (16-bit/32-bit word order — the endless compatibility bug: state your 32-bit word order explicitly), scaling, units, valid ranges, and behavior on write-out-of-range.
- Timing: slave response within the master's timeout budget (typically 100 ms–1 s); never do flash writes or blocking work mid-request — queue and respond, apply asynchronously.
- TCP: port 502, multiple simultaneous masters handled explicitly, MBAP transaction ID passthrough.
- Multi-drop: unit ID addressing, only the addressed slave responds; test with other traffic on the bus.

## 3. RS-485 Network Engineering

- Topology: daisy-chain only (no stubs >0.3 m); 120 Ω termination at both physical ends; bias resistors (fail-safe) at one node or transceiver built-in; common-mode range ±7 V — for longer runs or separate power domains, isolated transceivers.
- Cable: twisted pair, characteristic impedance ~120 Ω (Belden 9841 class); shield grounded at one end (or via cap at far end).
- Node count: 32 unit loads classic, up to 128/256 with fractional-load transceivers — state the loading math.
- Baud vs. length: 115200 → ≤100 m sane; 9600 → 1 km. Derate for noise; industrial default 9600/19200.
- Firmware: DE/RE timing (assert before first start bit, release after last stop bit + margin), bus-idle detection, collision-free single-master discipline.

## 4. CANopen / CAN in Automation

- CAN physical: 120 Ω both ends, bit timing calculated and shown (see communication-protocols.md §4); isolated transceivers in industrial.
- CANopen objects: EDS/DCF file is the device contract — produce it, keep it versioned; NMT state machine (pre-operational/operational/stopped), heartbeat producer (consumer monitors loss → fault reaction), PDO mapping for cyclic data, SDO for config, EMCY objects for diagnostics.
- Node-ID and baud set via LSS or hardware switches — document the provisioning method.
- J1939 (vehicles): PGN/SPN addressing, address claim procedure, DM1 diagnostics.

## 5. Industrial Ethernet: EtherCAT, PROFINET, EtherNet/IP

- These are certifications as much as protocols: conformance testing (ETG, PI, ODVA respectively) is required to sell into the ecosystem — budget it.
- EtherCAT: slave needs an ESC (e.g., Beckhoff ET1100/LAN9252) — you don't bit-bang EtherCAT on a plain MCU; real-time cycle 100 µs–1 ms, distributed clocks; firmware is object dictionary + process data sync.
- PROFINET RT: needs a PROFINET stack (often on dedicated modules — Anybus, Hilscher netX, or MCU-native on some Sitara/STM32MP); GSDML file is the contract; device naming/IP provisioning via DCP.
- EtherNet/IP: EDS file, explicit (config) + implicit (cyclic I/O) connections, CIP objects; ODVA conformance.
- Practical engineering: unless the product IS the protocol device, integrate a certified comms module (Anybus CompactCom, Hilscher netRAPID, HMS) — it owns the real-time stack and certification; your MCU talks to it over UART/SPI. This is the standard industrial shortcut: say when you recommend it.

## 6. IO-Link

- Point-to-point sensor/actuator link over standard 3-wire (M12/M8), 24 V signaling; COM2 (38.4 kbaud) most common.
- Device side: IO-Link device stack on a transceiver (e.g., TI TIOL111, Maxim MAX14828); IODD file (XML) describes parameters/process data — the contract you author.
- Value: remote parameterization, diagnostics, device replacement without config (master restores parameters) — implement the parameter server correctly; it's the feature customers buy.

## 7. OPC UA and MQTT Sparkplug (IT/OT Boundary)

- OPC UA: server on the device/gateway; information model (nodes, types) designed deliberately; security: X.509 certs, sign+encrypt policies; resource-heavy — gateway-class hardware (Linux SBC, raspberry-pi.md §4–5) or embedded UA SDK on bigger MCUs.
- MQTT Sparkplug B: the industrial MQTT convention — topic grammar (`spBv1.0/group/NBIRTH/edge`), birth/death certificates, metric aliases, protobuf payload. If the device feeds SCADA/IIoT platforms (Ignition), speak Sparkplug, not raw MQTT.
- Store-and-forward at the edge: OT networks partition; historical data backfill (OPC UA HA / Sparkplug rebirth with history) — buffer per iot-firmware.md §4.

## 8. Time Synchronization (PTP/NTP)

- NTP: ±ms over decent networks — fine for logs and SCADA timestamps; implement with monotonic-clock discipline (iot-firmware.md §4).
- PTP (IEEE 1588): ±µs with hardware timestamping (MAC/PHY support required — check the MCU/PHY); needed for coordinated motion, sampled-measurement correlation, protection relays.
- TSN (time-sensitive networking) over industrial Ethernet: scheduled traffic + time sync — awareness-level: if the customer says TSN, the switch/network is theirs; your device needs PTP hardware support and bounded-latency design.
- Document the device's time source, accuracy, and behavior on sync loss (holdover, drift rate, timestamp validity flags) in the ICD.


---


## FILE: references/iot-firmware.md

# IoT Firmware: Architecture, Cloud, Security, Lifecycle

## Contents
1. Reference architecture
2. Device identity and provisioning
3. Security requirements
4. Cloud connectivity design
5. Data pipeline design
6. Power management for IoT
7. Fleet operations and lifecycle

---

## 1. Reference Architecture

Layered design for any connected device:

```
Application logic (state machines, business rules)
Services: OTA, logging, config manager, health monitor, time sync
Connectivity: MQTT/CoAP client, provisioning, offline buffer
Middleware: sensor drivers, protocol stacks, storage (FS/kv-store)
HAL / board support
Hardware: MCU, sensors, radio, power
```

Rules: dependencies point downward only; application never touches hardware directly; every service has an init/health-report/shutdown interface so the health monitor can supervise it.

## 2. Device Identity and Provisioning

- Every device gets a unique identity at manufacture: device cert/key in secure storage (secure element like ATECC608 or MCU TrustZone/flash protection), or at minimum a unique ID + per-device secret.
- Provisioning flows (pick and document one): factory-injected certs, claim-based (device presents claim cert, cloud issues operational cert), BLE/soft-AP onboarding for consumer devices.
- Never ship a shared fleet-wide credential. One compromised device must not compromise the fleet.
- Manufacturing data to store per device: serial, hardware revision, calibration data, cert/key provisioning record — all with CRC and version.

## 3. Security Requirements (Minimum Bar)

- TLS 1.2+ (or DTLS for UDP) for all WAN traffic; validate server certificates; pin CA or broker cert where feasible.
- Signed OTA images verified by the bootloader (see microcontrollers.md §6) — unsigned update capability is the #1 fleet-killer.
- Secure boot where the hardware supports it (ESP32, STM32U5, nRF91/53): at minimum enable flash readout protection in production.
- Debug ports: lock or disable JTAG/SWD/UART shells in production builds; UART shell behind authentication if retained for service.
- Secrets never in source/firmware strings extractable from flash dump: use secure storage or at least obfuscation + readout protection.
- Rate-limit and authenticate any local control interface (BLE, AP mode).
- Threat model before coding: list assets (credentials, user data, control authority), attackers (casual, determined, supply-chain), and map each countermeasure to a threat.

## 4. Cloud Connectivity Design

- Connection state machine: `INIT → PROVISIONING → CONNECTING → CONNECTED → BACKOFF → (FALLBACK)`. Exponential backoff with jitter, capped (e.g., 5 min), persisted across reboots so a misconfigured device doesn't hammer the broker after every watchdog reset.
- Offline behavior is a first-class feature: define buffer capacity (flash wear-aware), eviction policy (oldest-first vs. lowest-priority-first), and upload catch-up strategy.
- Time: sync via NTP/cloud timestamp before timestamping data; handle absence of RTC (monotonic counter + boot-time anchor).
- Topic/endpoint design: `org/device-type/device-id/telemetry|event|cmd`; document the full topic schema and payload contracts in the ICD.
- Commands from cloud: idempotent, sequence-numbered, acknowledged; reject stale/replayed commands.

## 5. Data Pipeline Design

- Sampling vs. reporting decoupling: sample at the rate the physics needs; report at the rate the bandwidth/battery allows; aggregate (min/max/avg) in between when appropriate.
- Payload: versioned, compact (see communication-protocols.md §10); include device timestamp, sequence number, and firmware version in every packet — this makes fleet debugging possible.
- Edge intelligence: where ML/detection runs on-device, version the model like firmware (model ID in telemetry), and define fallback behavior when the model is absent/corrupt.
- Data quality flags: every measurement carries validity bits (sensor fault, stale, calibrated/uncalibrated) rather than dropping bad data silently.

## 6. Power Management for IoT

- Budget first: build a power table — sleep current × sleep time + wake current × wake time + radio TX energy per report = average current → battery life. Show this calculation; target with ≥30% margin.
- Duty-cycle radios aggressively; sensor warm-up times (gas sensors, radar) often dominate the energy budget — measure, don't assume.
- Event-driven wake (interrupt from sensor/RTC) beats periodic polling wherever possible.
- Measure actual sleep current on hardware: leftover peripherals, floating GPIO, and debug UART commonly add 100× leakage — verify against the budget table.

## 7. Fleet Operations and Lifecycle

- Observability from day one: device sends boot report (reset cause, firmware version, signal quality), periodic health metrics (heap free, stack watermark, reconnect count, sensor fault counters), and crash dumps (core dump to flash, upload after reconnect).
- OTA fleet strategy: cohort rollout (1% → 10% → 100%) with automatic halt on elevated failure metrics; never fleet-wide same-time updates on battery devices (power/network storm).
- Configuration management: cloud-side desired state vs. device-reported state; device must converge safely and persist config with CRC.
- End-of-life: define cert rotation, key expiry, and decommissioning behavior.
- Production test: every unit gets end-of-line test (sensor stimulus, radio loopback/RSSI check, current measurement, provisioning write) with results logged against serial number.


---


## FILE: references/manufacturing-lifecycle.md

# Manufacturing, Test Engineering, and Product Lifecycle

Industrial products ship for 10–15 years. Design decisions that ignore manufacturing and lifecycle become expensive surprises. This file covers what happens after the prototype works.

## Contents
1. Design for Test (DFT)
2. Production test: ICT, FCT, end-of-line
3. Programming and provisioning fixtures
4. Serialization, calibration, and traceability
5. Component lifecycle: obsolescence and second-sourcing
6. Long-lifecycle firmware maintenance
7. RMA and field service loop

---

## 1. Design for Test (DFT)

- Test points: every rail, every bus (I2C/SPI/UART/CAN), reset, boot straps, programming pins — on a pogo-pin grid (2.54 mm pitch) on the board's accessible side; sized ≥1 mm pads.
- Controllability/observability: firmware test mode that forces outputs, reports inputs, loops back comms, and reads ADCs on demand — design the manufacturing test protocol (UART command set) as a product feature, versioned like any other interface.
- Test-mode security: factory commands locked after provisioning (or behind a per-device key) — an open test backdoor in field units is a security finding.
- Boundary scan (JTAG) for high-pin-count parts when ICT access is limited — awareness-level; most MCU products rely on FCT instead.

## 2. Production Test: ICT, FCT, End-of-Line

- **ICT (in-circuit test)**: bed-of-nails verifies solder joints and component values before power — for volume products at contract manufacturers; requires the test-point discipline of §1. Skip for low volume (flying probe alternative).
- **FCT (functional circuit test)**: the fixture powers the board, flashes firmware, and runs the manufacturing test protocol: rails within tolerance, current consumption in window, each peripheral exercised, each output driven and measured (fixture has sense circuits), each input stimulated.
- **End-of-line (EOL) in enclosure**: final assembly test — full system function, radio/RSSI check, leak/IP test if sealed, label + serial verification.
- Test spec as a document: per-test limits with rationale (e.g., "sleep current <15 µA — catches solder bridges and missing load switches"), golden-sample correlation, and false-fail budget (a 2% false-fail rate at volume = a full-time rework job).
- Log everything per serial number (§4) — the test database is your field-failure correlation goldmine.

## 3. Programming and Provisioning Fixtures

- Production flashing: gang programmer or probe-based SWD/JTAG via the fixture; script the full sequence: erase → flash bootloader+app → set option bytes/RDP → verify → provision per-device data → final verify. One command, logged.
- Provisioning per device (see iot-firmware.md §2, firmware-security.md §3): unique serial, keys/certs (from a controlled key ceremony, HSM where warranted), factory calibration, hardware revision. Never a shared image with embedded credentials.
- Cycle time engineering: flashing+test time limits line throughput — minimize (compressed images, parallel fixtures, skip redundant verifies) and measure it.
- Golden unit policy: one unit per batch kept as reference; firmware images archived with hash so any shipped unit's bits can be reproduced byte-identically years later.

## 4. Serialization, Calibration, and Traceability

- Serial scheme: encode date/site/revision (e.g., YYWW-site-seq) in a format the label, the firmware, and the database all agree on; barcode/QR on the unit.
- Per-device calibration (sensors.md §4): fixture applies reference stimulus, firmware computes and stores calibration with CRC + version; the calibration record is logged to the database against the serial — retrievable for the device's whole life.
- Traceability record per serial: PCB batch, assembly batch, firmware hash, test results, calibration, provisioning record, ship destination. Field failure → query the cohort (same batch/site/date) before it becomes a recall.

## 5. Component Lifecycle: Obsolescence and Second-Sourcing

- Industrial lifetime 10–15 years vs. component lifecycles of 3–7: mismatch is the norm. At design time: check each critical part's lifecycle status (active/not-for-new-design/EOL), prefer vendors with longevity programs (ST 10-year, TI, Microchip, industrial lines), avoid consumer-trend parts.
- Second-source audit at Gate 1: every critical part has a pin-compatible alternative or a documented redesign risk; single-sourced custom parts (connectors, displays, modules) flagged with a mitigation (last-time-buy budget, redesign escrow).
- PCN/EOL monitoring: subscribe to vendor notifications; process: assess impact → qualify alternative or last-time-buy → update AVL/BOM revision → regression test (a "compatible" replacement still gets tested — timing and behavior differ).
- Firmware hedge: keep drivers for the alternative parts behind config switches where practical — a mid-life component swap becomes a config change, not a crisis.

## 6. Long-Lifecycle Firmware Maintenance

- Reproducible builds forever: containerized toolchain (toolchains-platformio.md §5), archived source+tools+docs per release — you must be able to rebuild a 10-year-old image to debug a field unit.
- Branching strategy: maintenance branch per released major version; security fixes back-ported deliberately; field firmware diversity tracked (which cohorts run what).
- OTA as the maintenance lifeline: the update mechanism must outlive protocol and cloud changes — versioned payloads, backward-compatible bootloaders, and never an OTA path that can orphan devices (see microcontrollers.md §6, firmware-security.md §5).
- Deprecation policy: cloud endpoints, certs (expiry dates! — a 5-year cert kills a 10-year product), crypto algorithms (migrate before they're broken, e.g., TLS version floors rising) — review on a schedule, not on failure.

## 7. RMA and Field Service Loop

- RMA process: return → extract black-box data BEFORE any reflash (debugging-methodology.md §5) → failure classification → 8D report for systemic issues → feed corrective action back to design/test.
- Failure Pareto: classify returns (solder, component, design, misuse, no-trouble-found); NTFR >30% usually means the test plan and the field environment disagree — revisit fault-injection coverage (reliability-testing.md §3).
- Service firmware path: authorized diagnostic/reflash flow for locked devices (firmware-security.md §6) — designed before the first locked unit ships.
- Spare parts and repairability: modular design where service replaces modules, not boards; conformal-coated boards are depot-repair, not field-repair — say so in the service manual.


---


## FILE: references/microcontrollers.md

# Microcontrollers: Selection, Configuration, Boot & OTA

## Contents
1. MCU selection matrix
2. Clock and power configuration
3. Startup, reset causes, and memory layout
4. Peripherals configuration rules
5. RTOS patterns
6. Bootloaders and OTA updates

---

## 1. MCU Selection Matrix

Choose by constraints, in priority order: power → real-time needs → peripherals → toolchain/ecosystem → cost.

| Family | Core | Best for | Watch-outs |
|---|---|---|---|
| STM32F1/F4/G4 | Cortex-M3/M4 | General industrial, motor control | F1 has known errata; check silicon rev |
| STM32L4/U5 | Cortex-M4/M33 | Battery devices (down to ~nA sleep) | Complex clock tree — validate wake times |
| ESP32 / ESP32-S3 / C3 | Xtensa / RISC-V | Wi-Fi/BLE IoT | RF coexistence affects timing; brown-outs on TX spikes — size PSU for 500 mA peaks |
| nRF52/nRF53 | Cortex-M4/M33 | BLE-first, ultra-low power | SoftDevice timing constraints; flash write stalls radio |
| RP2040 / RP2350 | Dual M0+/M33 | Cheap, PIO for custom interfaces | No internal flash — QSPI XIP latency, boot dependency on external flash |
| AVR (ATmega) | 8-bit | Simple control, legacy | Limited RAM; no memory protection |
| HK32 / CH32 / GD32 | M3/M4/RISC-V clones | Cost reduction | Register-level differences from ST originals; verify every peripheral against the actual datasheet |
| MSP430 / STM8 | 16/8-bit | Ultra-low power metering | Slow; weak debug tooling |

Selection checklist: Flash ≥ 2× application size (for OTA dual-bank), RAM ≥ 1.5× peak usage, ADC resolution/ENOB, number of timers/UARTs, operating temperature grade, package and pin count, supply voltage range vs. sensor levels, availability/second-source.

## 2. Clock and Power Configuration

- Validate the full clock tree: HSE/LSE failure fallback must be configured; USB needs ≤0.25% clock accuracy.
- Document worst-case MCU current in every mode: run / sleep / stop / standby, plus radio TX peaks. Size the supply and decoupling for peaks, not averages.
- Decoupling: 100 nF per power pin + 4.7–10 µF bulk per rail; radios need extra bulk near the antenna feed switch.
- Configure brown-out reset (BOR/BOD) at the highest level below minimum operating voltage; a device that runs unreliably at 2.1 V is worse than one that resets cleanly.
- Level shifting: never drive a 5 V-tolerant assumption without checking the datasheet; use proper level shifters on I2C/UART between voltage domains.

## 3. Startup, Reset Causes, and Memory Layout

- Read and log the reset-cause register at boot (power-on, watchdog, brown-out, software, pin). Persist it to retained RAM or flash before clearing.
- Define the memory map explicitly in the linker script: bootloader region, application A/B slots, config/calibration sector, log region. Document it in the spec.
- Initialize all peripherals to a known state before use — including de-initializing anything the bootloader left running (clocks, UART, DMA).
- Fill unused flash with a known pattern in production images to detect corruption.

## 4. Peripheral Configuration Rules

- **GPIO**: set unused pins to a defined state (analog input or pull) to cut leakage and noise; never leave floating outputs driving external circuits.
- **ADC**: respect sampling-time vs. source impedance; add RC anti-alias filtering; average in hardware or oversample when ENOB matters; calibrate with the internal reference where available.
- **Timers/PWM**: define dead time for H-bridges; verify resolution at the actual clock (show the calculation).
- **DMA**: mind cache coherency on Cortex-M7 (clean/invalidate D-cache or use non-cacheable buffers); handle half-transfer and error interrupts.
- **Interrupts**: set priorities deliberately — use the full NVIC priority map, never leave everything at default. Radio and motor-control interrupts get the top slots.

## 5. RTOS Patterns

Quick rules here; the deep reference is [rtos.md](rtos.md) (decision framework, primitive usage, ISR handoff, Zephyr specifics, debugging, anti-patterns).

- Use RTOS (FreeRTOS/Zephyr) when: ≥3 concurrent activities, a network stack, or strict separation of timing domains. Use super-loop when the logic fits one loop with ISRs.
- Task rules: one task per timing domain; communicate via queues, never shared globals without protection; size every stack with watermark measurement, then add ≥30% margin; enable stack-overflow checking and runtime stats in debug.
- Use tickless idle for battery devices; measure actual sleep current to confirm entry.
- Interrupt priorities: on Cortex-M, keep RTOS-aware ISRs at or below `configMAX_SYSCALL_INTERRUPT_PRIORITY`.

## 6. Bootloaders and OTA

- Architecture: bootloader + two application slots (A/B) or single slot + download area. Bootloader must be minimal, never update itself in the field, and must validate (CRC + signature) before every boot, not just after update.
- Update flow: download → verify signature (ECDSA/RSA with device-trusted public key) → verify CRC → set pending flag → reboot → bootloader swaps/validates → mark good only after the application self-tests. Roll back automatically on watchdog reset during trial boot.
- Power-fail safety: the swap must be resumable after power loss at any point (journal or swap-by-index with scratch area).
- Anti-rollback: monotonic version counter in protected storage.
- Differential updates only if bandwidth demands it — full-image dual-bank is simpler and safer.
- ESP32: use the native OTA partition scheme; nRF52: MCUboot/DFU; STM32: custom or MCUboot port. Always test OTA failure paths (kill power at 10%, 50%, 99%, during swap).


---


## FILE: references/micropython.md

# MicroPython and Arduino C++: Managed/Rapid Firmware Done Right

## Contents
1. Where MicroPython fits (and where it doesn't)
2. MicroPython performance discipline
3. MicroPython production architecture
4. MicroPython deployment and OTA
5. Arduino C++ language patterns
6. Graduating prototype code to production

---

## 1. Where MicroPython Fits (and Where It Doesn't)

- Fits: gateways/HMI, sensor hubs with relaxed timing (≥10 ms), business-logic-heavy IoT nodes, education, field-configurable devices, rapid product validation. Ports: ESP32 (best supported), RP2040/RP2350, STM32, nRF52.
- Doesn't fit: hard real-time (<1 ms jitter), tight power budgets (interpreter idle draws mA — light/deep sleep exists but wake cost is higher), safety-relevant control, small flash/RAM parts (<256 KB RAM is painful).
- Rule: real-time path in C (module or PIO/hardware peripheral), policy in Python. If you find yourself fighting the interpreter for timing, that's C's job.

## 2. MicroPython Performance Discipline

- Memory is the constraint: allocation causes GC pauses (ms-scale) — preallocate buffers (`bytearray`, `memoryview`), reuse objects in hot loops, avoid string building in loops (write into buffers; `ustruct.pack_into`).
- `micropython.native` decorator: ~2× speed; `micropython.viper`: near-C for integer code with typed pointers — use for protocol parsers, CRCs, bit-packing.
- Const data: `micropython.const()` for all constants — saves RAM per use.
- Interrupt handlers: use `micropython.schedule()` to defer work out of the ISR; hard IRQ handlers must not allocate (no exceptions, no object creation).
- Measure with `gc.mem_free()`/`micropython.mem_info()` in the test suite; call `gc.collect()` deliberately at idle points to control pause timing; `gc.threshold()` to reduce collection frequency.
- Async: `uasyncio` for concurrent network/sensor loops — one event loop, cooperative tasks; never mix blocking socket calls with uasyncio tasks.

## 3. MicroPython Production Architecture

- Freeze application modules into firmware (`.mpy` or frozen manifest build) — RAM stays free (frozen code runs from flash), boot is fast, and the filesystem holds only config/data.
- Structure like C: `main.py` = thin bootstrap (recovery mode check, watchdog start) → imports app modules; hardware access wrapped in driver classes with `init/deinit`.
- Watchdog: `machine.WDT` fed only by the health supervisor, same policy as C (reliability-testing.md).
- Exceptions: top-level catch-all logs to flash file + resets — an uncaught exception in the field must leave evidence (`sys.print_exception` to a rotated log).
- Recoverability: safe-mode boot (hold button / N failed boots → skip app, run REPL/maintenance mode); `boot.py` checks the flag before starting the app.

## 4. MicroPython Deployment and OTA

- Filesystem: littlefs2 (power-fail safe — the default on modern ports; FAT is not).
- OTA strategy: full firmware image via the port's OTA (ESP32: `esp32.Partition` OTA works from Python) for interpreter+frozen code; config/data updates as files. App-file-only updates are tempting but version-skew with the interpreter — prefer whole-image updates for products.
- Protect the REPL in production: disable UART REPL or gate behind authentication; WebREPL off.
- Versioning: report interpreter version + frozen app version + config version in telemetry.

## 5. Arduino C++ Language Patterns

The arduino.md file covers the platform; this is the language discipline for Arduino sketches that must not crash:

- Classes, not globals: wrap each peripheral in a class with `begin()`/`update()`; the sketch composes objects — testable, multi-instance, clean.
- `String` ban on AVR (heap fragmentation kills after days): fixed `char buf[N]` + `snprintf`; on ESP32/ARM with real RAM, `String` is tolerable but still avoid in hot loops.
- PROGMEM/flash strings: `F("literal")` on AVR; on ESP32 strings live in flash already.
- Non-blocking time: `millis()` subtraction state machines; `elapsedMillis` helper class acceptable; `delay()` allowed only in setup paths.
- Static allocation: declare objects globally or in static storage — avoid `new` except in init.
- Templates lightly: Arduino's compiler supports them, but heavy template metaprogramming explodes compile errors for marginal gain — keep to simple containers.
- Interrupt safety: `volatile` + `noInterrupts()/interrupts()` around multi-byte shared data — same rules as embedded-c.md §2.

## 6. Graduating Prototype Code to Production

Decision gate: product requirements (power, timing, certification, volume) vs. what the managed stack delivers. When graduating:
- MicroPython → C: port drivers first (same class API in C), keep Python for bring-up scripts and manufacturing test (it's excellent there).
- Arduino → native SDK: pin map, state machines, protocol code survive; replace library calls per arduino.md §5.
- Keep MicroPython/Arduino permanently for: manufacturing test fixtures, internal tools, demo units — that's legitimate production use, not a compromise.


---


## FILE: references/nrf.md

# Nordic nRF Series (nRF52, nRF53, nRF91) — nRF Connect SDK

## Contents
1. Family selection
2. nRF Connect SDK (NCS) essentials
3. SoftDevice vs. Zephyr Bluetooth
4. BLE production patterns
5. Power management (the reason you chose Nordic)
6. DFU and secure boot
7. Traps and failure modes

---

## 1. Family Selection

| Chip | Core | Radio | Use when |
|---|---|---|---|
| nRF52832 | M4F | BLE | Mature, cheap BLE peripheral |
| nRF52840 | M4F | BLE + 802.15.4 + USB | BLE flagship, Thread/Zigbee, USB needed |
| nRF52833 | M4F | BLE + 802.15.4, high temp | Direction finding, industrial temp |
| nRF5340 | Dual M33 | BLE 5.3 + 802.15.4 | New designs: app core + network core, TrustZone |
| nRF9160/9161 | M33 + modem | LTE-M/NB-IoT + GNSS | Cellular IoT; GNSS integrated |
| nRF52 + Arduino/Adafruit core | — | BLE | Prototyping only — graduate to NCS for products |

## 2. nRF Connect SDK (NCS) Essentials

- NCS = Zephyr RTOS + Nordic modules + MCUboot, built with west + CMake. Pin the NCS version (e.g., v2.x) per project; NCS versions change APIs between releases — upgrading is a task, not a drop-in.
- Build system: `west build -b <board>`; board targets for nRF53/nRF91 split cores (`nrf5340dk_nrf5340_cpuapp` / `_cpunet`).
- Configuration layers (understand all three or nothing works): Kconfig (`prj.conf` — software features), Devicetree overlay (`.overlay` — hardware/pin mapping), and Partition Manager (flash layout with MCUboot). Pin assignments live in devicetree, not `#define`s.
- Logging: Zephyr `LOG_*` macros with deferred logging; configure backends (UART/RTT) and levels per module in `prj.conf`.
- VS Code extension (nRF Connect for VS Code) is the reference IDE; command-line west works fine for CI.

## 3. SoftDevice vs. Zephyr Bluetooth

- Legacy nRF5 SDK uses SoftDevice (binary blob BLE stack). NCS uses Zephyr's open BLE host + Nordic controller. New designs: NCS. SoftDevice knowledge matters only for maintaining legacy products.
- Key SoftDevice-era constraints that still shape thinking: radio timeslots are owned by the stack — long ISRs or flash writes at the wrong time break connections.

## 4. BLE Production Patterns

- Roles: peripheral (sensor device) vs. central (gateway); define connection parameters explicitly — interval (7.5 ms–4 s), slave latency, supervision timeout (must be > (1+latency)×interval×2). State the values in the ICD.
- Throughput: negotiate MTU (default 23 B → 247 B with DLE); use notifications with connection interval tuned to data rate; write-with-response only for commands needing reliability.
- Bonding/security: use `BT_SECURITY_L2`+ for anything with user data; store bonds persistently (Zephyr settings subsystem on flash — mind write wear).
- Advertising: use extended advertising for >31 B payloads; manage advertising restart after disconnect; implement directed advertising for fast reconnect to known centrals where needed.
- nRF5340: BLE runs on the network core — application talks via HCI IPC; firmware updates must update both cores (see §6).
- Test at range edge: PER, reconnection after supervision timeout, behavior during peer's OTA.

## 5. Power Management (the reason you chose Nordic)

- System ON sleep with full RAM retention is the default idle — current in µA range with RTC running; System OFF (~0.4–1 µA) for longest sleep, wake only via GPIO/NFC/reset.
- Configure unused pins to disconnected/analog; a single floating input driven mid-rail costs more than the entire sleep budget.
- HFCLK only runs when needed (radio, some peripherals) — audit `nrf_power` / clock requests; a forgotten HFCLK request = mA instead of µA.
- DC/DC converter: enable (`CONFIG_SOC_DCDC_NRF52X`) for radio efficiency — requires the inductor on the board; verify the hardware has it.
- Measure with PPK2 (Power Profiler Kit II) — Nordic's own tool; measure the actual sleep current and connection-event average, compare to the budget table.
- BLE battery math: average current ≈ (event energy × events/s + sleep current); show this calculation with actual measured event charge.

## 6. DFU and Secure Boot

- MCUboot is the standard bootloader in NCS: signed images (imgtool, ECDSA-P256), swap-using-move or overwrite-only modes, downgrade protection via security counter.
- Flash layout via Partition Manager: MCUboot + primary app + secondary slot + settings/storage. Document the map.
- BLE DFU: MCUmgr + SMP over BLE (nRF Connect Device Manager app for testing); supports image upload, confirm, and reset. Always test: interrupted transfer (resume works), power loss mid-swap (rollback), unsigned image (rejected).
- nRF5340: dual-image update (app core + network core) — update the network core first, validate, then app core; use the provided multi-image DFU flow.
- nRF91: modem firmware and application firmware are separate DFU targets — modem DFU via the application's flash area; document both procedures.
- Production: lock the debug port (APPROTECT/CTRL-AP) after programming; provide an authorized recovery procedure.

## 7. Traps and Failure Modes

- Flash writes (settings, bonds, FDS) stall the CPU ~ms-scale — during a BLE connection event this breaks timing; schedule writes between events or accept connection parameter slack.
- GPIOTE + PPI: use hardware event routing for timing-critical pin reactions; GPIO interrupt latency through Zephyr is not deterministic enough for µs timing.
- Zephyr thread stacks: size via `CONFIG_MAIN_STACK_SIZE` etc. and measure with thread analyzer; overflow = cryptic faults.
- `printk` in ISRs floods and breaks timing — deferred logging only.
- Devicetree vs. reality: if a peripheral "does nothing," first check it's enabled in the overlay (`status = "okay"`) and pinctrl is assigned.
- Regulatory: Nordic modules carry modular approvals — keep the reference antenna/layout (see antenna-rf.md §6).


---


## FILE: references/pcb-layout.md

# PCB Layout for Embedded Products

Layout is where schematic intent meets physics. Most EMI, ADC noise, and RF failures are layout failures.

## Contents
1. Stackup and design rules
2. Placement strategy (before routing)
3. Grounding and return paths
4. Decoupling and power routing
5. Mixed-signal rules
6. High-speed and RF rules
7. High-current and thermal
8. Design review checklist and DFM

---

## 1. Stackup and Design Rules

- 2-layer: acceptable for simple low-speed boards — route ground as a grid, keep loops tiny, expect to work harder.
- 4-layer (SIG-GND-PWR-SIG) is the product default: unbroken ground plane under everything pays for itself in EMI and debug time.
- Set the fab's design rules into the CAD first (min trace/space, via drill, annular ring) — designing to rules you can't manufacture is scrap.
- Controlled impedance only matters for RF (see antenna-rf.md) and fast buses (USB 90 Ω diff) — get the fab stackup, compute widths, document.

## 2. Placement Strategy (Before Routing)

- Place by function block, following the schematic sheets: power → MCU → crystal → radio → sensors → connectors. Connectors are fixed by enclosure/mechanics first.
- Crystal: adjacent to MCU, shortest possible symmetric traces, guard ground, nothing under it.
- Decoupling caps: at the pins they serve — a 100 nF 5 mm away is decoration.
- Buck converter: input cap → IC → inductor → output cap as one tight cluster; hot loop (switch node) area minimized.
- Sensors: away from heat sources (regulators, MCU at full tilt, battery charger) — a temperature sensor 5 mm from an LDO reads the LDO. IMU away from connectors/board flex points (stress = offset).
- Antenna zone per vendor layout — sacred ground (antenna-rf.md §3).
- Test points and programming pads accessible for the production fixture (hardware-review.md §3).

## 3. Grounding and Return Paths

- Every signal has a return current directly beneath it on the ground plane — never route a signal over a plane split; the return detour is the EMI antenna.
- Star/split grounds: for mixed-signal, keep analog and digital return regions separate by placement (not by cutting the plane — splits cause more problems than they solve in 90% of designs); join at one point near the ADC/reference.
- Via stitching: ground vias at layer transitions of signals (return path follows), around the board edge (~λ/20 or few-mm grid) forming a Faraday cage edge, dense stitching around RF sections.
- Connectors: chassis/ESD ground separate from signal ground, joined via cap + R, TVS returns to chassis ground — ESD current must not traverse the logic ground.

## 4. Decoupling and Power Routing

- Per-pin 100 nF X7R within 2 mm, short via to plane; bulk 10–100 µF per power entry; radio modules get their own bulk per vendor app note.
- Power traces sized for current: 1 oz copper ≈ 0.5 mm/20 mil per amp (external layers, modest rise) — use a calculator, state the assumption; use planes or polygons for anything >500 mA.
- Keep switching regulator loops away from analog/RF: separate the buck's hot loop physically; inductor is a field emitter — shielded type, not under the antenna.
- Sense lines (feedback, current sense) routed quiet: away from switch nodes, kelvin-connected at the shunt.

## 5. Mixed-Signal Rules

- ADC inputs: short, over ground, no parallel run with digital clocks; RC filter at the ADC pin; reference decoupled per datasheet (often specific cap+ferrite).
- Clocks (crystal, MCU clock out, SPI/SDIO): short, over solid ground, via-stitched guard for aggressors near analog.
- USB/SDIO/high-speed: length-match where the spec demands (USB D+/D− skew, SDIO modest), controlled impedance where spec'd, no stubs.
- Level shifters placed at the domain boundary they serve.

## 6. High-Speed and RF Rules

- RF section replicates the module reference layout exactly — copy the keep-outs, feed line width, via fences (antenna-rf.md §2–3).
- Series R placeholders (22–47 Ω) on fast digital outputs (SPI, clocks) near the driver — rise-time control when EMI shows up.
- No routing under the antenna keep-out on ANY layer; battery/metal/display clearance respected.
- ESD: TVS within mm of the connector, short fat ground return; ESD current path never crosses the board.

## 7. High-Current and Thermal

- Motor/relay/heater currents: wide polygons, heavy copper option (2 oz), connector current rating with 2× margin per pin (parallel pins for more).
- Thermal: copper pours as heatsinks with via arrays under thermal pads (θJA math from circuit-design.md §2); hot parts away from temperature sensors and electrolytics (their lifetime halves per 10 °C).
- Creepage/clearance for mains voltages: slots under optos/relays, spacing per the voltage class — this is a safety item, not a preference.

## 8. Design Review Checklist and DFM

Run before fab, with evidence:
- [ ] Every net from schematic accounted for (no "R6 pin 1 NC by accident")
- [ ] All decoupling at pins; all bulk caps placed per §4
- [ ] No signal crosses a plane split; return vias at layer changes
- [ ] Crystal/switch-node/antenna zones clean per §2/§6
- [ ] Power trace widths verified vs. current (math in notes)
- [ ] Test points on all rails + key signals; programming pads on grid for pogo fixture
- [ ] Silkscreen: pin-1 marks, polarity marks, connector labels, board rev
- [ ] Fiducials (3) if machine-assembled; panelization/tooling holes per assembler
- [ ] DRC clean with the fab's rule set; 3D fit check against enclosure CAD
- [ ] Thermal: thermal-pad via arrays present; hot parts placed per §7
- [ ] DFM export: gerbers + drill + pick-and-place + centroid verified (view them yourself — don't trust the export)


---


## FILE: references/raspberry-pi.md

# Raspberry Pi: RP2040/RP2350 (Pico) and Linux SBCs in Embedded Systems

## Contents
1. RP2040/RP2350 (Pico) — microcontroller use
2. PIO — the killer feature
3. Pico traps and failure modes
4. Raspberry Pi (Linux SBC) in embedded products
5. Linux-side rules for reliability
6. MCU + SBC hybrid architectures

---

## 1. RP2040/RP2350 (Pico) — Microcontroller Use

- RP2040: dual Cortex-M0+ @ 133 MHz, 264 KB RAM, **no internal flash** — boots from external QSPI flash (XIP). RP2350: M33 or RISC-V cores, more RAM, TrustZone option.
- Toolchain: Pico SDK (CMake + GCC, C/C++) or MicroPython/CircuitPython; Arduino core exists (arduino-pico) for prototyping. Pico SDK is the production path.
- No EEPROM/flash filesystem by default: reserve flash regions (via linker or `PICO_FLASH_SIZE_BYTES`) for config; wear is on the external flash — plan a filesystem (littlefs) or wear-aware kv-store for frequent writes.
- Boot: ROM bootloader → UF2 drag-and-drop for dev; production flashing via SWD (Picoprobe/debug probe) or custom bootloader over UART/USB.
- Dual core: core 1 must be launched explicitly (`multicore_launch_core1`); shared data needs critical sections/spinlocks; both cores share the XIP flash — heavy flash access stalls both.

## 2. PIO — the Killer Feature

- PIO = programmable I/O state machines (2 blocks × 4 SMs on RP2040) that bit-bang custom protocols cycle-exact, independent of CPU: WS2812/NeoPixel, DMX, custom SPI variants, quadrature encoders, VGA, software UARTs/I2S, high-rate ADC capture.
- Use PIO whenever a protocol has tight timing that would otherwise burn a core or demand ISRs with impossible latency budgets.
- PIO programs are written in PIO assembly (`pioasm`); test them standalone (the SDK has PIO examples; logic-analyzer-verify the timing).
- DMA + PIO pairing: stream data to/from PIO FIFOs via DMA — CPU-free data movement; handle FIFO under/overrun IRQs.

## 3. Pico Traps and Failure Modes

- **External flash dependency**: QSPI layout and quality matter; XIP latency affects ISRs — time-critical code goes in RAM (`__not_in_flash_func`); flash erase stalls everything (same rule as all single-flash MCUs).
- **No hardware brown-out or RTC on RP2040**: add external supervisor/RTC if the product needs them; RP2350 improves this.
- **USB**: TinyUSB stack — composite devices work; respect 1 ms SOF timing, don't block in USB callbacks.
- **3.3 V only, not 5 V tolerant** — level-shift everything from 5 V domains.
- **ADC is mediocre** (DNL issues, ~9 ENOB): for precision analog use an external ADC.
- **Watchdog**: enable (`watchdog_enable`); scratch registers survive watchdog reset — use them to pass reset-cause/diagnostics across the reboot.

## 4. Raspberry Pi (Linux SBC) in Embedded Products

Appropriate roles: gateway, edge ML inference, HMI, protocol bridge — not hard real-time control (Linux kernel latency is unbounded without PREEMPT_RT, and even then it's ms-class).
- Use the Compute Module (CM4/CM5) for products, not the consumer board: eMMC instead of SD, proper thermal design, IO board control.
- SD-card-based Pi in a product = guaranteed field failures: SD corruption from power cuts. Mitigate: read-only rootfs + overlayfs, separate data partition with journaling, or move to eMMC/CM.
- Power: Pi 4/5 need clean 5 V/3–5 A; voltage dips cause SD corruption and USB dropouts — use a proper PMIC design and undervoltage logging (`vcgencmd get_throttled`).
- Peripherals: UART/I2C/SPI via device tree overlays; the mini-UART (ttyS0) baud drifts with core clock — use PL011 (ttyAMA0) for reliable serial.

## 5. Linux-Side Rules for Reliability

- **Read-only or resilient filesystem**: the #1 Pi field failure is filesystem corruption from uncontrolled power loss. Read-only rootfs, tmpfs for /var/log, data partition with f2fs/ext4-journal, or an industrial SLC eMMC.
- **Watchdog**: enable the BCM hardware watchdog (`/dev/watchdog` + watchdog daemon) — reboots a hung Pi; test it by actually hanging the system.
- **Service supervision**: run the application under systemd with `Restart=always`, start-limit, and dependency ordering; log via journald with size caps.
- **Graceful shutdown**: if power can be cut, add a UPS HAT/supercap + GPIO power-fail signal that triggers `shutdown` within the hold-up time; otherwise accept corruption risk and design the filesystem for it.
- **OTA/fleet updates**: use a proven updater (RAUC, Mender, SWUpdate) with A/B partitions — never `apt upgrade` a fleet.
- **Thermal**: Pi throttles at 85 °C; monitor `vcgencmd measure_temp` and log throttle events; design enclosure thermals for worst case.
- **Security**: change default credentials, disable password SSH (keys only), lock down unused services, firewall the WAN side; sign updates.

## 6. MCU + SBC Hybrid Architectures

Best-practice split for IoT products: MCU (Pico/STM32/ESP32) does real-time sensing/control and power management; Pi does connectivity, storage, ML, and UI.
- Inter-processor link: UART (with framed protocol + CRC — see communication-protocols.md §1) or SPI (MCU as slave); define the ICD: command set, versioning, flow control, error handling.
- Power orchestration: MCU controls Pi power (load switch), wakes on events, boots Pi only when needed — cuts system power 10–50× for battery/hybrid devices; MCU supervises Pi watchdog and force-cycles it.
- Firmware update path: Pi updates MCU firmware over the link (define the MCU bootloader protocol; verify + rollback as always).
- Failure isolation: MCU must keep safe-state control running if the Pi crashes — never route safety-critical control through Linux.


---


## FILE: references/real-time-analysis.md

# Real-Time Analysis: Schedulability, Latency, and Resource Budgets

## Contents
1. Timing requirement capture
2. Rate Monotonic Analysis (RMA) — the math
3. Interrupt latency budgeting
4. WCET estimation and measurement
5. Priority inversion and its cures
6. Memory budgeting methodology

---

## 1. Timing Requirement Capture

Build the timing table at Gate 1 — every periodic activity:

| Task/ISR | Period | Deadline | Est. WCET | Priority | Justification |
|---|---|---|---|---|---|
| radio_isr | event, ≤2 ms bursts | 500 µs | 80 µs | highest | RX FIFO overflow at 1 Mbps |
| motor_ctl | 1 ms | 1 ms | 120 µs | high | current loop stability |
| sensor_poll | 100 ms | 50 ms | 2 ms | medium | filter Nyquist |
| telemetry | 60 s | 5 s | 400 ms | low | cloud contract |

A deadline without a measured worst case is a guess. Schedule this table, then verify on hardware (§4).

## 2. Rate Monotonic Analysis (RMA) — the Math

- Assign priorities: shortest period = highest priority (rate-monotonic). For fixed-priority preemptive scheduling this is optimal.
- Utilization bound (Liu & Layland): U = Σ(Ci/Ti) ≤ n(2^(1/n) − 1) ≈ 0.69 for large n. **Keep total CPU utilization ≤0.7** for comfort margin; above it, do exact response-time analysis.
- Exact response-time test (per task i): iterate R = Ci + Σ_ceil(R/Tj)·Cj over higher-priority j until stable; require R ≤ deadline.
- Include ISRs as highest-priority "tasks" in the utilization sum — they consume CPU too.
- Blocking term B (worst time a lower-priority task holds a needed resource) adds to every response time: R = Ci + Bi + Σ…. Keep critical sections microseconds-short.
- Show this calculation in the architecture document for any system with ≥3 concurrent timing activities.

## 3. Interrupt Latency Budgeting

Total latency = hardware entry (~12 cycles Cortex-M) + max interrupt-disabled section + higher-priority ISR execution + (RTOS: critical sections). Measure the worst interrupt-disabled span:
- Audit every `__disable_irq()`, RTOS critical section, and driver lock; time them (cycle counter / scope on a GPIO).
- Budget example: radio needs ≤500 µs service; worst disabled span 40 µs + worst higher ISR 60 µs → margin 5×. State it.
- Cortex-M tail-chaining and late-arrival reduce real latency; a bad NVIC priority assignment destroys it — assign priorities deliberately (radio > motor > comms > housekeeping).

## 4. WCET Estimation and Measurement

- Estimation: count instructions on the worst path with caches/flash-wait-states considered (XIP flash and cache misses inflate 10–50× — measure instead).
- Measurement (do this, always): DWT cycle counter (CYCCNT) around the code, or GPIO toggle + oscilloscope/logic analyzer. Run the worst-case stimulus (max payload, worst branch, flash erase concurrent), record max over ≥10⁴ runs.
- Report WCET as measured-max × 1.5 safety factor, and put the number in the timing table.
- Beware "usually fast" traps: malloc, printf, floating point, string ops, flash writes, TLS handshakes — all have long tails.

## 5. Priority Inversion and Its Cures

- Scenario: low task holds mutex; medium task preempts; high task blocked on mutex → high effectively runs at medium priority.
- Cures: priority inheritance mutexes (FreeRTOS `xSemaphoreCreateMutex` has it — plain binary semaphores do NOT; Zephyr mutexes do); keep critical sections short; prefer lock-free single-writer queues; never take a mutex in an ISR.
- Deadlock audit: document lock ordering; a mutex taken in two different orders across the codebase is a time bomb.

## 6. Memory Budgeting Methodology

At Gate 1, produce and track:

| Resource | Budget | Method to verify |
|---|---|---|
| Flash | app ≤60% of slot (OTA headroom) | linker map file per build; CI check |
| Static RAM (.data+.bss) | ≤50% | map file |
| Stacks | measured watermark +30% | `uxTaskGetStackHighWaterMark` after soak |
| Heap | high-water +30%, or zero (static only) | `xPortGetMinimumEverFreeHeapSize` / mallinfo |
| Retained/no-init | explicit region | linker script review |

- Read the map file on every release build — sudden growth = scope creep or accidental debug code.
- Stack sizing is measured, never guessed: watermark after a soak covering worst-case call depth (deepest: fault handler during printf during TLS).
- Flash wear budget: writes/day × expected life years × cycles-per-write vs. flash endurance (typ. 10k–100k); add wear-leveling factor. Show the math for any device writing logs/config daily.


---


## FILE: references/reliability-testing.md

# Reliability, Testing, and Pre-Production Verification

## Contents
1. Watchdog and fault handling
2. Defensive coding standards
3. Test strategy (unit → HIL → fault injection)
4. EMI/EMC hardening
5. Environmental and power testing
6. Pre-production checklist

---

## 1. Watchdog and Fault Handling

- Window watchdog preferred over simple watchdog; refresh only from a dedicated supervisor after every subsystem reports healthy (heartbeat flags from each task/ISR domain).
- On watchdog reset: preserve RAM diagnostics (no-init section), log reset cause + last heartbeat states, then enter degraded-safe mode if the fault repeats (N consecutive watchdog resets → safe state, alert, wait for recovery command).
- Hard fault handler: capture stacked registers (PC, LR, xPSR, fault status/address registers like CFSR/HFSR/BFAR on Cortex-M), store to flash/no-init RAM, then reset. A device that silently reboots is undebuggable in the field.
- Assert policy: debug build = trap + breakpoint; release build = log + controlled recovery. Never ship handlers that just `while(1)`.
- Define safe-state for the product: what do outputs (relays, motors, heaters, valves) do on any fault? Default must be the fail-safe direction.

## 2. Defensive Coding Standards

- Compiler: `-Wall -Wextra -Werror`; add `-Wshadow -Wconversion` for new code. MISRA-C:2012 subset for safety-relevant C; run a static analyzer (PC-lint, clang-tidy, cppcheck) — zero warnings policy.
- No dynamic allocation after init in long-running devices (fragmentation); use static/pool allocation.
- Check every return value; mark intentional ignores explicitly.
- Integer discipline: fixed-width types, explicit signedness, overflow-checked arithmetic for time (handle tick wraparound — `if ((int32_t)(now - deadline) >= 0)` pattern).
- Shared data: volatile + critical sections or lock-free single-writer patterns; document every ISR/task shared variable.
- Version everything: firmware semantic version, build hash, hardware revision — readable via debug interface and reported to cloud.

## 3. Test Strategy

### Unit tests (host-compiled)
- All pure logic (parsers, filters, state machines, CRC, protocol framing) compiles and runs on the host with a framework (Unity, CppUTest, Google Test). Target ≥80% coverage on logic modules.
- State machines get transition-table-driven tests: every state × every event, including illegal ones.

### Hardware-in-the-loop
- Driver tests on real hardware: sensor present/absent, boundary reads, timing verification.
- Automated: script-driven flashing + UART-output assertion, run per commit.

### Fault injection (mandatory before "flawless" claims)
Run and document results for:
- Unplug each sensor mid-operation → system detects, degrades, recovers on replug
- Corrupt packets (bit flips, truncation, replay) → CRC rejects, counters increment, no crash
- Kill power during flash write / OTA swap at random points ×20 → device always boots a valid image, config never corrupt
- Brown-out sweep (variable PSU, slow ramp 0→VDD) → BOR holds reset until valid voltage, no runaway
- I2C bus held low (slave fault simulation) → recovery sequence restores bus
- Wi-Fi/broker outage 24–72 h → buffering, backoff, recovery without reboot loop
- 72 h+ soak test at full functionality → no memory leak (heap watermark stable), no counter rollover, no drift
- Temperature extremes (if spec'd): cold boot at min temp, continuous run at max temp

### Timing/resource verification
- Measure: worst-case ISR latency, task stack watermarks (all tasks ≥30% free), heap high-water, boot time, sleep current, radio TX current. Compare against budget table — every number documented.

## 4. EMI/EMC Hardening (Firmware + Hardware Co-Design)

- Firmware measures that survive ESD/EFT events: watchdog (always), periodic re-init of critical peripherals (I2C/SPI peripherals lock up after transients), RAM scrubbing or periodic re-verification of critical config (SEU resilience).
- External watchdog / supervisor IC for anything controlling hazardous loads.
- Debounce all external inputs in firmware (buttons, interrupt lines) — ESD on cables causes phantom interrupts; count and rate-limit interrupt storms.
- Unused interrupt vectors point to a handler that logs and returns — never default to hanging.
- Hardware: ESD diodes on external connectors, common-mode chokes on wired buses leaving the board, series resistors on long GPIO runs.

## 5. Environmental and Power Testing

- Power: test with the actual battery/PSU, including weak battery (internal resistance rises → voltage sags on TX bursts → spurious resets; add bulk capacitance or reduce TX power at low battery).
- Mains-powered: test with relay/motor loads switching nearby — conducted transients are the classic field failure.
- RF devices: test at the edge of coverage, during hand/body proximity, inside the final enclosure (see antenna-rf.md §7).
- Thermal: verify no component exceeds rating at max ambient + full load; firmware should implement thermal derating where relevant (reduce TX power, throttle sampling).

## 6. Pre-Production Checklist

Apply before declaring any firmware production-ready. Every item must have evidence (test log, measurement, or code reference):

**Boot & Recovery**
- [ ] Reset cause logged and recoverable from field devices
- [ ] Watchdog active, refresh policy documented, fault-escalation path tested
- [ ] Hard fault handler captures context to persistent storage
- [ ] OTA rollback verified with power cuts at every phase

**Code Quality**
- [ ] Zero compiler warnings at `-Wall -Wextra -Werror`
- [ ] Static analysis clean (or every warning justified in writing)
- [ ] No magic numbers; every register config cites datasheet
- [ ] Version/build info embedded and readable

**Resources**
- [ ] Stack watermarks ≥30% free on all tasks (measured, soak-tested)
- [ ] Heap high-water documented; no leaks over 72 h soak
- [ ] Flash/RAM headroom ≥20%
- [ ] ISR latency measured within budget

**Peripherals & Sensors**
- [ ] Every external input range-checked
- [ ] Every blocking operation has a timeout
- [ ] Sensor fault detection + recovery tested per sensor
- [ ] Calibration stored with CRC + factory fallback

**Communications**
- [ ] CRC/framing validation on every protocol
- [ ] Reconnect/backoff state machines tested with real outages
- [ ] Offline buffering behavior verified (capacity, eviction, catch-up)

**Power & Environment**
- [ ] Current budget measured and matches calculation in all modes
- [ ] Brown-out tested with slow voltage ramps
- [ ] Sleep current measured (not calculated) on final hardware
- [ ] Operation verified at temperature extremes if spec'd

**Security & Production**
- [ ] Debug ports locked in production build
- [ ] No shared fleet credentials; secure storage for keys
- [ ] Signed OTA enforced; unsigned image rejected (tested)
- [ ] End-of-line production test defined and documented


---


## FILE: references/requirements-fmea.md

# Requirements Engineering and FMEA for Firmware

## Contents
1. Writing testable requirements
2. Requirement ID system and traceability
3. FMEA methodology (the core elite practice)
4. Fault trees and hazard analysis
5. Common requirement mistakes

---

## 1. Writing Testable Requirements

A requirement is only valid if a test can prove or disprove it. Transform vague statements:

| Vague | Testable requirement |
|---|---|
| "low power" | REQ-PWR-003: Average current ≤15 µA over a 10-min reporting cycle, measured at 3.6 V, 25 °C |
| "fast response" | REQ-TIM-001: Button press to actuator output ≤50 ms, 99th percentile, over 1000 trials |
| "reliable connection" | REQ-COM-002: After any network outage ≤72 h, device reconnects within 5 min of restoration and uploads ≥99% of buffered samples |
| "accurate temperature" | REQ-SEN-001: ±0.5 °C over 0–50 °C after 2-point calibration, verified against reference thermometer at 5 points |
| "robust" | REQ-REL-001: Device recovers to full function without manual intervention after any single sensor disconnect/reconnect |

Every requirement needs: ID, statement with number + condition + tolerance, priority (MoSCoW), verification method (test/analysis/inspection/demonstration), and source (user request/assumption/derived).

## 2. Requirement ID System and Traceability

- Prefixes: `REQ-FUN` (function), `REQ-TIM` (timing), `REQ-PWR` (power), `REQ-ENV` (environment), `REQ-COM` (communications), `REQ-REL` (reliability), `REQ-SEC` (security), `REQ-SAF` (safety), `REQ-MFG` (manufacturing).
- Traceability matrix (keep in the spec, update every gate):

| Req ID | Implemented in | Verified by | Status |
|---|---|---|---|
| REQ-PWR-003 | power.c:enter_sleep() | TEST-PWR-101 (PPK2 measurement) | PASS 2024-… |

- A requirement without a test is a wish. A test without a requirement is scope creep. Match them both ways.
- Changes: requirement changes get versioned with rationale; re-run affected tests (the matrix tells you which).

## 3. FMEA Methodology (the core elite practice)

For every component/function, enumerate failure modes systematically. Severity (S), Occurrence (O), Detection (D) on 1–5; RPN = S×O×D; attack highest RPN first.

| ID | Item | Failure mode | Effect | S | O | D | RPN | Mitigation (detection → response) |
|---|---|---|---|---|---|---|---|---|
| FM-001 | Temp sensor | Open circuit | Reads full-scale | 3 | 2 | 1 | 6 | Range-check → mark invalid, use last-good ≤5 min, then degrade to safe-state |
| FM-002 | I2C bus | SDA stuck low | All bus devices dead | 4 | 2 | 3 | 24 | Bus-hang detect (timeout) → SCL pulse recovery → power-cycle sensor rail → system reset as last resort |
| FM-003 | Flash | Power cut during config write | Corrupt config | 4 | 3 | 1 | 12 | Double-buffer + CRC → revert to last-good copy, log event |
| FM-004 | Wi-Fi | Outage 72 h | Data loss | 3 | 3 | 1 | 9 | Ring buffer sized for 96 h → oldest-first eviction only at overflow |
| FM-005 | Relay output | MCU hangs with output ON | Heater stuck on | 5 | 2 | 2 | 20 | External watchdog + hardware failsafe (relay defaults OFF on reset; gate drive requires periodic refresh pulse) |
| FM-006 | Battery | Deep discharge | Device unrecoverable in field | 4 | 2 | 2 | 16 | Fuel gauge + low-battery cutoff at 3.0 V, ship-mode below threshold |

Rules:
- Include software failure modes (stack overflow, priority inversion, counter rollover at 49.7 days, buffer full) — not just hardware.
- Include the failure mode "works perfectly but with wrong data" (miscalibration, swapped sensor channels) — the most dangerous class, because nothing looks broken.
- For every S≥4, mitigation must be **hardware or independent-path** — the same MCU that failed cannot be its own only safeguard.
- After mitigation, re-score: document residual RPN and why it's acceptable.
- The FMEA directly generates: the graceful-degradation table, the fault-injection test list, and the watchdog supervision list. If it doesn't, you did it as paperwork — redo it.

## 4. Fault Trees and Hazard Analysis

For top-level hazards ("device causes overheating", "device loses all data"), build a fault tree downward: hazard ← OR/AND gates ← contributing faults. Use it to find single points of failure: any fault that alone reaches the top event through an OR gate is a design liability — eliminate or add an independent barrier.

## 5. Common Requirement Mistakes

- Specifying implementation instead of behavior ("use FreeRTOS" vs. "meet these deadlines") — constrain implementation only when there's a real reason (team skill, certification, existing IP).
- Missing negative requirements: what the device must NOT do (never actuate during OTA, never log PII, never draw >1 mA in ship mode).
- Missing operational envelope: temperature, supply voltage, vibration, humidity — and behavior outside it (must fail safely, not silently).
- Unbounded requirements ("always", "never", "100%") — bound everything ("≥99% over 10⁴ operations").
- Forgetting lifecycle requirements: manufacturability, calibratability, updatability, diagnosability, decommissioning.


---


## FILE: references/rtos.md

# RTOS Deep Reference: FreeRTOS, Zephyr, and Task Design

## Contents
1. Do you need an RTOS? (decision framework)
2. Task design patterns
3. FreeRTOS primitives — correct usage
4. ISR-to-task handoff patterns
5. Zephyr specifics
6. Configuration that matters
7. RTOS debugging playbook
8. Anti-patterns

---

## 1. Do You Need an RTOS? (Decision Framework)

- Super-loop + ISRs when: one timing domain, ≤2 concurrent activities, no network stack, team unfamiliarity is a real risk. Determinism is trivially provable.
- RTOS when: ≥3 concurrent timing domains, network/USB stacks, complex power management, multiple developers. Cost: priority inversion risk, stack management, harder WCET proof.
- Event-driven framework (QP/C, Zephyr SMF, protothreads) when: many states, few threads — concurrency without stack-per-task cost.
- State the choice + justification in the Gate 1 architecture (real-time-analysis.md provides the schedulability math).

## 2. Task Design Patterns

- One task per timing domain, not per feature: `task_sensor` (100 ms), `task_comms` (event-driven), `task_ui` (50 ms), `task_housekeeper` (1 s: watchdog feeding, health checks, stats).
- Task anatomy: init phase → infinite loop blocking on queue/notification/period — never polling with `vTaskDelay(1)`.
- Priority assignment: rate-monotonic within task set (real-time-analysis.md §2); ISRs of course higher than any task; housekeeping lowest above idle.
- Stack sizing: measure watermark after soak, then ×1.3 minimum. Stack overflow = the #1 RTOS field failure — `configCHECK_FOR_STACK_OVERFLOW=2` in debug and first-production.
- Health supervision: each task sets its heartbeat bit each cycle; supervisor feeds the watchdog only when all bits set — a hung task must hang the watchdog, not get fed around.

## 3. FreeRTOS Primitives — Correct Usage

| Primitive | Use for | Traps |
|---|---|---|
| Task notification | ISR→task wake, light signaling (fastest, least RAM) | One pending value per task — not a queue |
| Queue | All multi-byte producer→consumer data | Copy semantics (large structs = slow: queue pointers); full-queue policy must be defined (drop oldest/newest/block-with-timeout) |
| Counting semaphore | Resource pools, ISR event counting | Not for mutual exclusion |
| Binary semaphore | Legacy signaling | Task notification is better in almost every case |
| Mutex | Shared resource exclusion | Has priority inheritance — binary semaphores DON'T (the classic inversion bug); never take in ISR |
| Recursive mutex | Rare — redesign instead | Hides call-structure problems |
| Event groups | Multi-condition sync (bits from several sources) | Bits are not data; consumer must re-read state |
| Stream/message buffers | Byte streams ISR↔task (UART TX/RX) | Single writer/single reader only |
| Software timers | Periodic light duties, timeouts | All timer callbacks share one task — keep callbacks tiny; never block |

- Timeouts everywhere: `xQueueReceive(..., portMAX_DELAY)` only where blocking forever is correct by design; everything else gets a bounded timeout + error path.
- `FromISR` variants in interrupts only; `portYIELD_FROM_ISR()` when a wake occurred.

## 4. ISR-to-Task Handoff Patterns

- Pattern A (data): ISR reads hardware → `xQueueSendFromISR` → task processes. For UART/SPI/ADC-complete.
- Pattern B (event): ISR → `vTaskNotifyGiveFromISR` → task does the hardware read. Lower ISR latency, task bears the register access.
- Pattern C (deferred work): heavy processing → pended function or dedicated high-priority worker task.
- Rule: ISR duration budgeted (real-time-analysis.md §3); DMA does bulk movement; the task owns protocol logic. Never parse protocols, call printf, or allocate in an ISR.

## 5. Zephyr Specifics

- Model: threads + workqueues + kernel objects, configured by Kconfig — hardware by devicetree. Read nrf.md §2 for the config layering.
- Threads: static stacks via `K_THREAD_STACK_DEFINE` + `k_thread_create`, or `K_THREAD_DEFINE`; system workqueue for small deferred jobs (never block it).
- Sync: `k_msgq` (queues), `k_sem`, `k_mutex` (priority inheritance), `k_event`, ring buffers for ISR byte streams; `k_poll` for multi-source waits.
- Power: PM subsystem + device runtime PM — tickless is native; device drivers must implement suspend/resume for real sleep currents.
- Logging: `LOG_INF/ERR` deferred — never `printk` in ISRs (timing) — see nrf.md §7.
- Choose Zephyr when: nRF (native), multi-vendor portability target, rich subsystems needed (USB, BLE host, filesystems, shell). FreeRTOS when: minimal footprint, vendor SDK is FreeRTOS-based (ESP-IDF), team already fluent.

## 6. Configuration That Matters (FreeRTOS)

- `configUSE_PREEMPTION=1`, `configUSE_TIME_SLICING=0` for deterministic systems (same-priority round-robin hides bugs).
- `configMAX_PRIORITIES` small (5–8) — forces deliberate priority economy.
- `configMAX_SYSCALL_INTERRUPT_PRIORITY`: every ISR calling FreeRTOS API at/below it — wrong value = rare corruption (the hardest bug class).
- `configASSERT` enabled in debug: catches API misuse at the call site.
- `configCHECK_FOR_STACK_OVERFLOW=2`, `configUSE_MALLOC_FAILED_HOOK=1`, `configRECORD_STACK_HIGH_ADDRESS=1`.
- Tick rate: 100 Hz is plenty for most (1 kHz burns power and shrinks time-slice granularity benefits); tickless idle for battery.
- Heap scheme: heap_4 (coalescing) if dynamic allocation unavoidable; heap_1 or static-only (`configSUPPORT_STATIC_ALLOCATION`) for long-running products.

## 7. RTOS Debugging Playbook

- Deadlock: dump task states (blocked on what?) via `vTaskList()`/debugger RTOS-aware view (J-Link Ozone, STM32CubeIDE FreeRTOS view); check mutex ordering violations.
- Priority inversion: high task delayed while low runs → find the mutex, confirm inheritance, shorten critical section.
- Stack overflow: watermark audit; enable overflow hook that logs task name.
- Missed deadlines: SystemView/Tracealyzer trace — compare actual schedule vs. the Gate 1 timing table; look for surprise blockers (mutexes, full queues, flash writes).
- CPU load: `vTaskGetRunTimeStats` (needs a fast timer configured); idle-task hook counter as poor-man's load meter.

## 8. Anti-Patterns (Reject in Review)

- Task-per-message-type proliferation (10+ tasks, each with own stack, all mostly idle) — merge into domain tasks.
- Polling loops with `vTaskDelay(1)` instead of blocking on an event.
- printf/UART TX inside mutex held across the whole transfer.
- Queues of large structs (copy cost) — queue pointers to pool buffers instead.
- `portMAX_DELAY` everywhere: no timeouts = undiagnosable hangs.
- FreeRTOS API from ISR without `FromISR`, or from ISRs above `configMAX_SYSCALL_INTERRUPT_PRIORITY`.
- Shared globals "because it's faster than queues" — the audit pattern from embedded-c.md §2 applies.
- Software timers doing real work (they serialize in one task).
- Creating/deleting tasks at runtime in long-running products (fragmentation + error paths) — create all at init.


---


## FILE: references/safety-standards.md

# Safety Standards and Certification Awareness for Firmware

## Contents
1. When standards apply
2. IEC 60730 Class B (appliances) — the most common
3. IEC 61508 / functional safety basics
4. MISRA C practical adoption
5. Certification pathway and documentation
6. Domain quick map

---

## 1. When Standards Apply

- The product controls something that can hurt people or property (heaters, motors, mains, medical, automotive) → safety analysis is mandatory thinking even if formal certification isn't.
- Certification is a market decision: household appliances (IEC 60730), industrial (IEC 61508), automotive (ISO 26262), medical (IEC 62304), rail (EN 50128). Determine at Gate 0 — retrofitting safety is 10× the cost.
- Even without formal certification, apply the engineering practices: single-fault tolerance, self-tests, defensive monitoring. This file gives awareness-level guidance; formal certification requires notified bodies and licensed tools — say so when the user's project is headed there.

## 2. IEC 60730 Class B (appliances) — the Most Common

Class B = software intended to prevent hazards in appliances. Firmware requirements (self-tests run periodically, typically at startup and/or during operation):
- **CPU registers test**: stuck-at test of registers.
- **Program counter test**: watchdog + logical program-flow monitoring.
- **Interrupt handling test**: verify interrupts fire at expected rates (counter cross-check).
- **Clock test**: independent reference comparison (e.g., LSI vs. HSE ratio check on STM32).
- **Flash integrity**: CRC over code memory, periodic or at boot.
- **RAM test**: March pattern or checkerboard, non-destructive during operation (test in slices) or full at boot.
- **Stack test**: overflow detection (guard patterns).
- **Peripheral tests**: ADC plausibility (known reference channel), GPIO read-back, comms CRC.

Vendor libraries: ST X-CUBE-CLASSB (STM32), certified Class B libraries exist for most major MCUs — use them rather than writing your own; they come with certification evidence. Design consequence: the safe state must be reachable when any self-test fails — the FMEA safe-state table and the Class B failure handler are the same mechanism.

## 3. IEC 61508 / Functional Safety Basics

- SIL 1–4 by risk; firmware contributes via systematic capability: development process rigor, diagnostics (diagnostic coverage % — the fraction of dangerous failures your self-tests catch), and hardware fault tolerance.
- Key firmware patterns: dual-channel/diverse processing for safety functions, monitored watchdogs (windowed, external), safe-state enforcement, proven-in-use or certified components (RTOS, libraries).
- An independent safety channel (the safety function does not depend on the MCU running the main app) is the strongest pattern — often a supervisor IC or second small MCU.
- If the user's product is SIL-rated: state clearly that formal assessment, certified toolchain, and safety lifecycle documentation are required — assist with the engineering, don't imply the skill's output is "certified."

## 4. MISRA C Practical Adoption

- MISRA C:2012 (+AMD) — the de facto safe C subset. Practical adoption tiers:
  - Tier 1 (every project): no undefined behavior enablers — fixed-width types, no out-of-bounds, no unbounded loops without exit proof, switch has default, no dynamic memory misuse.
  - Tier 2 (professional): run a checker (cppcheck `--addon=misra`, PC-lint, Coverity); zero unmitigated violations; deviations documented with rationale in code comments.
  - Tier 3 (certified): full compliance report as certification evidence.
- Pair with CERT C for security-adjacent rules.
- Coding standard beyond MISRA: define and enforce naming (module_prefix_function), one module = one .c/.h, header guards, no globals without justification, const-correctness.

## 5. Certification Pathway and Documentation

Typical flow: hazard analysis → safety requirements (with integrity levels) → architecture meeting them → implementation under controlled process → verification with coverage metrics → assessment/audit. The documentation trail IS the product:
- Requirements traceability (see requirements-fmea.md) — certification auditors live in this matrix.
- FMEA/FMEDA (add diagnostic coverage numbers).
- Test plans with evidence; tool qualification records; configuration management (every binary traceable to sources).
- EMC and radio certifications (CE/FCC) run in parallel — see antenna-rf.md §6.
Budget reality: certification adds months and 5–6 figures; flag it in project estimates.

## 6. Domain Quick Map

| Product | Standards to check |
|---|---|
| Home appliance (heater, motor, mains) | IEC 60730 Class B, IEC 60335 |
| Industrial controller | IEC 61508, IEC 61131 (PLC) |
| Medical device | IEC 62304 (software lifecycle), ISO 14971 (risk), IEC 60601 (hardware) |
| Automotive | ISO 26262 (ASIL), AUTOSAR, MISRA mandatory |
| Battery-powered consumer | UN 38.3 (battery transport), IEC 62133 (battery safety) |
| Radio device | FCC/CE-RED, plus duty-cycle firmware rules (see antenna-rf.md) |
| Smart meter/utility | IEC 62052/62053, DLMS/COSEM |

State the applicable set at Gate 0; if unsure, list candidates and tell the user what to confirm with their compliance contact.


---


## FILE: references/sensors.md

# Sensors: Selection, Interfacing, Calibration, and Failure Modes

## Contents
1. Sensor selection by measurand
2. Interface design rules
3. Signal conditioning and filtering
4. Calibration and compensation
5. Failure modes and diagnostics
6. Common part-specific notes

---

## 1. Sensor Selection by Measurand

| Measurand | Common parts | Interface | Key spec to check |
|---|---|---|---|
| Temperature | DS18B20, TMP117, NTC thermistor, PT100/1000 | 1-Wire, I2C, analog | Accuracy across range, self-heating |
| Humidity | SHT31/45, HDC2080 | I2C | Condensation behavior, long-term drift |
| Pressure | BMP390, LPS22, MS5611 | I2C/SPI | Absolute vs. relative, noise floor |
| IMU/accel/gyro | MPU6050, LSM6DS3, BMI270, ICM-42688 | I2C/SPI | Noise density, offset drift, ODR |
| Magnetometer | LIS3MDL, BMM150 | I2C/SPI | Hard/soft-iron interference on PCB |
| ToF distance | VL53L0X/L1X/L4 | I2C | Range vs. target reflectivity, crosstalk |
| Ultrasonic | HC-SR04, waterproof JSN-SR04T | GPIO/PWM | Blind zone, beam angle |
| mmWave radar | Seeed MR60BHA2, IWR6843 | UART | Presence vs. fall-detection variant, mounting height constraints |
| Gas | MQ series, SGP30/40, SCD41 (CO2) | Analog/I2C | Burn-in time, cross-sensitivity, calibration gas |
| Current/voltage | INA219/226, ACS712, HLW8012 | I2C/analog | Isolation, shunt sizing |
| Optical/pulse | MAX30102 (PPG), TSL2591 | I2C | Ambient rejection, LED drive current |
| Biosignal | ADS1292 (ECG), MLX90614 (IR temp) | SPI/I2C | Medical-grade front-end requirements |
| Load cells | HX711 + strain gauge | Digital | Noise vs. sample rate, excitation stability |
| GNSS | u-blox NEO-M9/M10, Quectel L96 | UART | TTFF, antenna supply, PPS timing |

## 2. Interface Design Rules

- **I2C sensors**: verify pull-up sizing (show calculation: Rp min from sink current, Rp max from rise time with bus capacitance); scan the bus at boot and fail loudly if an expected address is absent; many cheap sensors hang the bus on power glitch — implement bus-recovery (9 clock pulses on SCL).
- **SPI sensors**: respect max clock, mode (CPOL/CPHA), and CS setup/hold; shared-bus sensors must tri-state MISO properly — verify or add series resistors.
- **Analog sensors**: buffer high-impedance sources; account for ADC input leakage; ratiometric sensors (strain gauge, some pressure) must share the ADC reference with the excitation.
- **UART sensors**: validate every frame (header, length, checksum); handle partial frames and garbage after power glitch; radar/CO2 sensors often stream continuously — drain the buffer or it overflows silently.

## 3. Signal Conditioning and Filtering

- Choose filter by noise spectrum, not habit: moving average for white noise reduction, median filter for spike rejection (glitches, ESD), exponential/IIR for smooth control signals, Kalman/complementary for IMU fusion.
- State filter parameters with sampling rate — a cutoff frequency without Fs is meaningless.
- Oversampling + decimation: each 4× oversample adds ~1 bit effective resolution; show the tradeoff in output data rate.
- Plausibility layer before the filter: reject readings outside physical range (e.g., temperature step >10 °C/s) before they contaminate the filter state.

## 4. Calibration and Compensation

- Every production device needs at minimum a single-point offset calibration stored in flash with CRC and a factory-default fallback.
- Two-point (offset + gain) for analog chains; temperature compensation table for pressure/gas/IMU where the datasheet gives drift coefficients.
- Never calibrate over the factory values — write to a separate calibration sector with versioning.
- Document the calibration procedure in the production runbook: stimulus, wait time, pass criteria, data stored.

## 5. Failure Modes and Diagnostics

Design for these explicitly — each needs a detection method and a defined system response:

- **Stuck value** (sensor returns identical reads): track a stale counter; reset power or re-init after N stale samples.
- **Bus lockup**: I2C recovery sequence; power-cycle sensor rail if available.
- **Out-of-range**: sensor disconnected (0 V, full-scale, NaN) vs. genuine extreme — distinguish open-circuit from valid reading (check pull behavior).
- **Slow drift**: baseline tracking for gas/PPG sensors; flag when recalibration is needed.
- **Power sequencing**: many sensors need defined power-up delay before first communication (check tBOOT in datasheet); first reads after wake are often garbage — discard per datasheet.
- **Self-test**: use built-in self-test bits (IMUs, pressure sensors) at boot where available.

## 6. Common Part-Specific Notes

- **DS18B20**: parasitic power is unreliable — use external VDD; conversion takes 750 ms at 12-bit — do not block.
- **HX711**: 80 SPS mode needs different clock count; power-down via PD_SCK high >60 µs.
- **MAX30102**: needs ambient-light subtraction and motion artifact rejection for any pulse reading; raw PPG without filtering is unusable.
- **MR60BHA2 (60 GHz radar)**: UART 115200, reports heart/breath rate only with stationary target within ~1.5 m; mounting orientation matters; validate against a reference device — do not treat output as medical-grade.
- **MQ gas sensors**: heater draws ~150 mA; require 24–48 h burn-in; readings are relative (Rs/R0) — cannot produce absolute ppm without calibration gas.
- **HC-SR04**: 5 V logic — level-shift the echo pin down to 3.3 V; echo timeout must be implemented (no object = no echo = infinite wait otherwise).
- **BME280/BMP390**: forced mode for battery devices; IIR filter coefficient changes effective response time — state it.


---


## FILE: references/stm32.md

# STM32 Family — HAL/LL, CubeMX, and Production Firmware

## Contents
1. Family selection
2. Toolchain: CubeMX / CubeIDE workflow
3. Clock tree and power rules
4. Peripheral traps (the flaws that bite)
5. DMA and interrupt architecture
6. Flash, bootloader, and protection
7. Debugging with SWD

---

## 1. Family Selection

| Series | Core | Focus | Notes |
|---|---|---|---|
| F0/G0 | M0/M0+ | Low cost | G0 is the modern F0 replacement |
| F1 | M3 | Legacy general | Old; many clones (GD32/CH32) differ subtly |
| F4 | M4F | Performance general | Workhorse; F405/F407/F411 common |
| G4 | M4F | Analog/motor | Fast ADCs, op-amps, HRTIM |
| L4/L4+/U5 | M4F/M33 | Low power | U5 adds TrustZone, best-in-class sleep |
| H7 | M7/M4 dual | High performance | Cache coherency complexity — see §5 |
| WB/WBA | M4+M0+ / M33 | BLE | Radio on second core, firmware via FUS — special update flow |
| WL | M4 | Sub-GHz LoRa | Integrated SX126x |
| MP1 | A7+M4 | Linux-capable | Different ecosystem entirely |

Rule: pick the cheapest series that meets ADC/timer/peripheral needs with 2× flash headroom; check the errata sheet for the exact part + silicon revision before design freeze.

## 2. Toolchain: CubeMX / CubeIDE Workflow

- CubeMX generates initialization code + `.ioc` project file. Commit the `.ioc` to version control — it is the hardware configuration of record.
- Generated code has `USER CODE BEGIN/END` sections: **all user code goes inside them** or a CubeMX regeneration silently deletes it. For anything non-trivial, keep CubeMX output as init-only and write drivers separately.
- HAL vs. LL: HAL for speed of development on complex peripherals (USB, ETH, SDMMC); LL or direct register for timing-critical paths (ADC+DMA, timers). Mixing is normal — document where and why.
- CubeIDE = Eclipse + GCC + ST-Link debugger; alternatives: Keil MDK (commercial, strong optimizer), IAR (commercial, safety cert options), plain arm-none-eabi-gcc + CMake (best for CI). See toolchains-platformio.md.
- Pin the CubeMX/HAL firmware-package version per project; HAL upgrades change behavior.

## 3. Clock Tree and Power Rules

- The clock tree is the most mis-configured part: validate every derived frequency (AHB/APB1/APB2/timer clocks — APB timers run at 2× when prescaler ≠1; USB needs exact 48 MHz; ADC max clock per datasheet).
- Use HSE (crystal) for anything needing UART accuracy at high baud or USB; HSI drifts with temperature — quantify baud error if you rely on it.
- `HAL_Delay()` depends on SysTick; if SysTick priority is misconfigured under RTOS, delays hang. Under FreeRTOS use `vTaskDelay`, and raise SysTick priority per the FreeRTOS STM32 port requirements.
- Low power: run/stop/standby/shutdown modes with very different wake sources and retention — state which peripherals stay clocked; RTC + LSE required for standby timekeeping; verify wake time budget (HSI startup, PLL relock) against application latency.
- Enable brown-out (BOR) and independent watchdog (IWDG, LSI-clocked — can't be stopped by software) for production.

## 4. Peripheral Traps (the flaws that bite)

- **I2C**: HAL blocking I2C in an ISR context deadlocks; I2C peripheral locks up on bus glitches — implement bus recovery (toggle SCL via GPIO bit-bang, re-init peripheral). Check errata for I2C on F1 (known issues).
- **UART**: overrun errors halt reception until ORE cleared — in the HAL, enable error callbacks and clear flags; use IDLE-line interrupt + DMA for variable-length protocols (the standard robust pattern).
- **ADC**: calibrate (`HAL_ADCEx_Calibration_Start`) after every clock change; sampling time vs. source impedance — long sampling time for high-impedance sources or readings bleed across channels; injected vs. regular conversions for motor control timing.
- **Timers**: update interrupt doesn't fire on first config without forcing an update event (UG bit) — classic "timer starts late" bug; PWM center-aligned mode changes frequency math (÷2).
- **USB**: needs 48 MHz ±0.25%; VBUS sensing pin config varies by board — wrong config = device never enumerates on some hosts.
- **F1 clones (HK32/GD32/CH32)**: register-compatible mostly, but flash wait states, ADC behavior, and USB differ — verify every peripheral against the clone's datasheet, never assume ST equivalence.

## 5. DMA and Interrupt Architecture

- Standard robust UART RX: circular DMA + IDLE interrupt, process in task — no per-byte interrupts.
- DMA on H7: D-cache coherency — either place DMA buffers in non-cacheable MPU regions (D2/D3 SRAM) or clean/invalidate cache around transfers. Forgetting this causes intermittent data corruption that appears "random."
- DMA priority vs. peripheral data rate: set very-high priority for ADC/audio streams; underruns/overruns are silent without error interrupts — enable them.
- NVIC: set priority grouping explicitly (`NVIC_PRIORITYGROUP_4` under FreeRTOS); every interrupt used with RTOS API calls must be at/below `configMAX_SYSCALL_INTERRUPT_PRIORITY` (numerically ≥ its value).

## 6. Flash, Bootloader, and Protection

- Flash write/erase stalls CPU on single-bank parts — never erase while real-time tasks run; execute flash routines from RAM where required.
- Option bytes: configure RDP level (readout protection L1 for production — L2 is irreversible), BOR level, IWDG hardware enable. Document the production option-byte programming step; verify with a test unit (RDP L1 blocks debugging — plan firmware signing-off before enabling).
- Custom bootloader layout: vector table relocation (`SCB->VTOR`) in the app; bootloader validates CRC before jump; app marks itself valid after self-test (see microcontrollers.md §6).
- Dual-bank parts (L4+, G4, H7 some) enable safe swap OTA — prefer them for field-updatable products.

## 7. Debugging with SWD

- ST-Link + SWD: keep SWD pins free in the pin map (don't reassign PA13/PA14); under low-power modes debug attach fails — document how to recover (connect-under-reset).
- `SWV`/ITM trace for printf-style debug without UART; ETM trace on larger parts via J-Trace for timing analysis.
- Semihosting is debug-only — strip from release builds (it hangs without a debugger attached on some configs).
- Fault diagnosis: on HardFault read SCB->CFSR/HFSR/BFAR/MMAR — implement a fault handler that logs these (see reliability-testing.md §1); CubeIDE's Fault Analyzer visualizes them.


---


## FILE: references/toolchains-platformio.md

# Toolchains, IDEs, and Build Systems for Embedded Development

## Contents
1. PlatformIO (the recommended cross-platform build system)
2. Vendor IDEs: STM32CubeIDE, nRF Connect (VS Code), ESP-IDF tools, Arduino IDE 2
3. Compilers: GCC ARM, LLVM/clang, IAR, Keil
4. Debuggers and probes: ST-Link, J-Link, Picoprobe, ESP-Prog
5. CI/CD for firmware
6. RF/wireless development tools (the "RF connect" stack)

---

## 1. PlatformIO

The default choice for multi-platform firmware projects (AVR, ESP32, STM32, nRF52, RP2040, 1000+ boards).

- `platformio.ini` is the single source of truth: platform, board, framework, build flags, library deps (pinned versions), upload/debug config, and **environments** (`[env:debug]`, `[env:release]`, `[env:production]` with different flags).
- Rules for production use:
  - Pin everything: `platform = espressif32@6.x.x`, `lib_deps = owner/lib@1.2.3` — never float versions.
  - Separate environments for debug/release: release sets `-Os`, strips debug, enables watchdog config; debug adds `-Og -g3` and asserts.
  - Use `extra_scripts` for version stamping (git hash → `build_flags`) so every binary reports its origin.
  - `build_unflags` to remove Arduino core defaults that hide warnings.
- Unit testing: `pio test` with Unity on native (host) env for logic + on-target env for drivers — integrate into CI.
- Debugging: PIO Unified Debugger works with ST-Link/J-Link/ESP-Prog; configure `debug_tool` per env.
- Limits: exotic vendor SDKs (full nRF Connect SDK features, ESP-IDF menuconfig depth) eventually outgrow PIO's abstraction — graduate to native toolchains when the project needs them.

## 2. Vendor IDEs

| IDE | Stack | Strengths | Watch-outs |
|---|---|---|---|
| STM32CubeIDE | CubeMX + Eclipse + GCC | .ioc config of record, Fault Analyzer, SWV/ITM trace | Regeneration overwrites non-USER-CODE sections |
| nRF Connect for VS Code | west + Zephyr + Kconfig | Reference NCS environment, devicetree/Kconfig GUIs, PPK2 integration | Steep config layering (Kconfig + devicetree + Partition Manager) |
| ESP-IDF (VS Code ext / Eclipse) | CMake + idf.py | menuconfig, partition tables, core-dump analysis, size analysis (`idf.py size-components`) | sdkconfig drift between machines — commit it |
| Arduino IDE 2 | arduino-cli | Fastest start, education | No version pinning rigor, no tests — prototype only |
| Keil MDK (µVision) | ARMCC/AC6 | Strong optimizer, RTX RTOS, safety certs | Commercial, Windows-only |
| IAR EWARM | IAR compiler | Best-in-class optimization, functional-safety certified editions | Commercial; migration cost from GCC |
| Segger Embedded Studio | GCC/clang + J-Link | Excellent debug experience, free for some Nordic use | — |
| Zephyr west + CMake (CLI) | Zephyr | CI-native, board-agnostic | Manual everything — but fully scriptable |

Rule: pick the vendor-native toolchain for production (deepest hardware support); use PlatformIO for multi-platform projects, rapid prototyping, and test automation.

## 3. Compilers

- **arm-none-eabi-gcc**: the default for Cortex-M. Use `-Os` for release, `-Og` for debug, `-ffunction-sections -fdata-sections + --gc-sections`, LTO only with testing (it exposes latent bugs — good, but budget the time). Always `-Wall -Wextra -Werror` + map file review.
- **clang/LLVM**: increasingly viable (Zephyr supports it); better diagnostics; check vendor HAL compatibility first.
- **ARMCC (Keil)/IAR**: tighter code on some targets, certified compilers for safety-critical (IEC 61508/ISO 26262 workflows) — use when certification requires tool qualification.
- Version-pin the compiler per project; record it in the build notes; a compiler upgrade is a change to the shipped binary — regression-test it.
- Understand your linker script: memory regions, section placement, stack/heap sizing symbols. Never ship with the vendor's default linker layout unreviewed.

## 4. Debuggers and Probes

- **ST-Link** (incl. on Nucleo): STM32 only, cheap, SWD + SWV.
- **J-Link**: universal Cortex-M + RISC-V; RTT (fast bidirectional debug channel over SWD — replace UART printf for timing-sensitive debug), Ozone/SystemView for RTOS-aware tracing. The professional default.
- **Picoprobe / debugprobe**: RP2040/RP2350 SWD; also flashes the Pico itself.
- **ESP-Prog / built-in USB-JTAG** (S3/C3): JTAG debugging + `openocd` for ESP32.
- **Logic analyzer** (Saleae, DSLogic, even a $10 Cypress FX2): non-negotiable for protocol bring-up — verify I2C/SPI/UART timing and framing on the wire before blaming code.
- **Oscilloscope**: power-rail ripple during radio TX, reset behavior, crystal startup, PWM edges.
- **Power profiling**: Nordic PPK2 or Joulescope — sleep-current verification is impossible with a multimeter alone.

## 5. CI/CD for Firmware

- Every commit: build all envs (warnings-as-errors), run host unit tests, archive the `.elf/.hex/.bin` + map file + git hash.
- Nightly: HIL test rig (self-hosted runner with a debug probe + target board): flash, run scripted tests, capture UART logs, report.
- Release pipeline: version bump → signed build (OTA image signing in CI, keys in HSM/secrets, never in repo) → artifacts + changelog → staged rollout hooks.
- Reproducibility: containerized toolchain (Docker image with pinned gcc/SDK versions) so any commit rebuilds bit-identically years later.
- Static analysis in CI: cppcheck/clang-tidy on every PR; MISRA checker if safety-relevant.

## 6. RF/Wireless Development Tools ("RF Connect" stack)

For BLE/RF development and validation:
- **nRF Connect for Desktop**: Bluetooth Low Energy app (GATT browser/server emulator), Programmer (flashing), Power Profiler (PPK2 UI), RSSI Viewer, Direct Test Mode app — the standard BLE dev toolkit.
- **nRF Connect for Mobile** (iOS/Android): field GATT testing, DFU over BLE via nRF Connect Device Manager.
- **Sniffers**: nRF52840 dongle + Wireshark plugin for BLE over-the-air capture; TI Packet Sniffer for sub-GHz/Zigbee; ESP32 Wi-Fi promiscuous capture. Air captures settle protocol disputes instantly.
- **VNA** (NanoVNA for hobby, proper VNA for production): antenna S11 verification — see antenna-rf.md.
- **Spectrum analysis**: TinySA for hobby pre-checks; certified lab gear for compliance.
- **Direct Test Mode (DTM)**: run the radio in continuous TX/RX test modes for PER measurement and pre-compliance — mandatory before claiming RF performance.
- For ESP32: `esp_rf` certification test firmware; for STM32WB/WL: vendor RF test modes. Document the DTM procedure in the production test plan.


---


## FILE: assets/templates/firmware-spec-template.md

# Firmware Specification — [Product Name]

Version: 0.1 | Date: YYYY-MM-DD | Status: DRAFT
Hardware: [MCU + part number, board rev] | Author: [name]

## 1. Overview
One paragraph: what the device does, for whom, in what environment.

## 2. Requirements
| ID | Requirement (number + condition + tolerance) | Priority | Verification | Source |
|---|---|---|---|---|
| REQ-FUN-001 | | Must | Test TEST-FUN-101 | user |
| REQ-PWR-001 | | Must | Measurement | derived |
| REQ-ENV-001 | Operating −20…+60 °C, fail safely outside | Must | Analysis + test | assumption |

## 3. Architecture
- Execution model: [super-loop / FreeRTOS / Zephyr] — justification:
- Layer diagram: application / services / middleware / HAL / hardware
- Execution contexts: tasks and ISRs with period, deadline, priority, est. WCET (see timing table)
- Schedulability: utilization U = ΣCi/Ti = [x] ≤ 0.7; response-time check for tasks above bound

## 4. State Machines
[System state machine: states, events, transitions, timeouts — diagram or table. One per peripheral where applicable.]

## 5. Memory Map and Budgets
| Region | Address/size | Contents |
|---|---|---|
| Bootloader | | |
| App slot A / B | | |
| Config/calibration (CRC'd, double-buffered) | | |
| Log / crash dump | | |
Budgets: Flash app ≤ [60%] of slot; static RAM ≤ [50%]; stacks measured +30%; flash-wear: [writes/day × years vs. endurance].

## 6. Power Budget
| Mode | Current | Duty | Energy contribution |
|---|---|---|---|
| Sleep | | | |
| Active | | | |
| Radio TX | | | |
Average current: [x] → battery life [y] on [battery] (≥30% margin). Measured values replace estimates after first hardware.

## 7. Interfaces
Reference: ICD document [interface-control-document.md] — buses, protocols, payloads, versions.

## 8. Failure Handling (from FMEA)
| Failure | Detection | Response | Safe state |
|---|---|---|---|
| (summary rows from fmea-worksheet.md, S≥3) | | | |

## 9. Security
Threat model summary: assets / attackers / countermeasures. Secure boot: [yes/no + chain]. Key storage: [secure element / eFuse / flash]. Debug lockdown: [plan].

## 10. Verification Plan
Reference: [test-plan-template.md]. Traceability matrix: REQ → code → test → status.

## 11. Manufacturing and Deployment
Flashing/provisioning procedure; per-device data (serial, keys, calibration); end-of-line test; OTA strategy and rollback; field diagnostics (black-box data retrieval).

## Appendix: Assumptions and Open Questions
Every assumption made without user confirmation, and every open question, listed explicitly.


---


## FILE: assets/templates/fmea-worksheet.md

# FMEA Worksheet — [Product Name]

Version: 0.1 | Date: YYYY-MM-DD
Scales: S/O/D 1–5 (S: 5 = hazard/data loss, 1 = cosmetic; O: 5 = certain in field, 1 = unlikely; D: 5 = undetectable until effect, 1 = detected immediately). RPN = S×O×D.

## Failure Modes
| FM ID | Item | Failure mode | Cause | Effect | S | O | D | RPN | Detection | Response / mitigation | Residual RPN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FM-001 | | | | | | | | | | | |

## Rules for Completing This Worksheet
- Include software failure modes: stack overflow, priority inversion, counter/tick rollover, heap exhaustion, buffer overflow, race conditions, watchdog starvation, corrupt flash, stale data.
- Include the "wrong data, nothing looks broken" class: miscalibration, swapped channels, unit errors, stale readings displayed as fresh.
- Include operational modes: during OTA, during low battery, during network outage, during sensor warm-up, at temperature extremes.
- S ≥ 4 requires an independent-path mitigation (hardware or separate channel), not just more code on the same MCU.
- Every row generates: one entry in the firmware-spec failure-handling table AND one fault-injection test in the test plan. Cross-reference the IDs.
- After mitigation, re-score O and D → residual RPN; justify every residual RPN ≥ 8 in the test plan's risk section.

## Single Points of Failure (from fault tree)
| Hazard | Faults that alone cause it (OR-gate) | Barrier added |
|---|---|---|


---


## FILE: assets/templates/interface-control-document.md

# Interface Control Document (ICD) — [Product Name]

Version: 0.1 | Date: YYYY-MM-DD

## 1. Physical Interfaces
| Interface | Signals | Voltage | Connector | Notes |
|---|---|---|---|---|
| UART0 (debug) | TX, RX, GND | 3.3 V | test points | 115200 8N1 |

## 2. Bus Configurations
### I2C Bus 0
- Speed: [100/400 kHz]; pull-ups: [value + calculation reference]; timeout: [ms]; recovery: SCL-pulse sequence on hang
| Device | Address | Role | Max rate |
|---|---|---|---|

### SPI Bus 0
- Mode: [0–3]; max clock: [MHz]; shared MISO: [yes/no]
| Device | CS pin | Mode | Max clock |
|---|---|---|---|

## 3. Protocol Definitions (one section per protocol)
### Protocol: [name] over [transport]
- Framing: [sync bytes + length + payload + CRC16 (poly 0x1021, init 0xFFFF)]
- Byte order: [little/big]; encoding: [packed struct / CBOR / JSON]; protocol version byte: [offset]
- Error handling: retries [n], backoff [schedule], timeout [ms]; invalid packet action: [drop + counter]

| Msg ID | Name | Direction | Payload format | Rate |
|---|---|---|---|---|

## 4. Wireless Contracts
- BLE: services/characteristics table (UUID, properties, max length, security level); connection parameters (interval/latency/timeout); MTU
- MQTT: topic schema `org/type/id/{telemetry|event|cmd}`, QoS per topic, payload schema + version
- LoRaWAN: region, class, DR/ADR policy, port map, duty-cycle budget

## 5. Payload Schemas
| Field | Offset/Key | Type | Unit | Range | Validity rule |
|---|---|---|---|---|---|
| version | 0 | uint8 | — | 1 | must equal current |

## 6. Versioning and Compatibility
- Protocol/payload version negotiation rule: [reject / degrade]
- Compatibility policy: [which versions interoperate]


---


## FILE: assets/templates/test-plan-template.md

# Test and Verification Plan — [Product Name]

Version: 0.1 | Date: YYYY-MM-DD | Firmware under test: [version/hash]

## 1. Unit Tests (host-compiled)
| Test ID | Module | Cases | Pass criteria | Result |
|---|---|---|---|---|
| TEST-UNI-001 | protocol parser | valid/invalid/truncated frames, CRC errors | all handled, no crash, counters correct | |

## 2. Hardware-in-the-Loop
| Test ID | Target | Setup | Cases | Result |
|---|---|---|---|---|
| TEST-HIL-001 | sensor driver | board + sensor on bench | present/absent/boundary reads, timing | |

## 3. Fault Injection (from FMEA — one test per FM-*)
| Test ID | FMEA ref | Injection | Expected behavior | Result |
|---|---|---|---|---|
| TEST-FI-001 | FM-002 | Hold SDA low mid-transfer | Detect ≤[x] ms, recover, zero lost reboots | |
| TEST-FI-002 | FM-003 | Power cut during config write ×20 | Last-good config always restored | |
| TEST-FI-003 | FM-004 | Broker outage 72 h | Buffer per spec, reconnect ≤5 min, ≥99% data | |
| TEST-FI-004 | — | OTA power cut at 10/50/99%/swap ×5 each | Valid image always boots | |
| TEST-FI-005 | — | Brown-out ramp 0→VDD slow ×10 | Clean reset, no flash corruption | |

## 4. Timing and Resource Measurements
| Metric | Budget | Measured | Method | Result |
|---|---|---|---|---|
| Worst ISR latency | | | GPIO + logic analyzer | |
| Stack watermark (each task) | ≥30% free | | RTOS API after soak | |
| Heap minimum ever free | | | | |
| Boot time to operational | | | | |
| Sleep current | | | PPK2/Joulescope | |
| Radio TX peak current | | | | |
| CPU utilization worst-case | ≤0.7 | | | |

## 5. Soak and Environment
| Test ID | Condition | Duration | Pass criteria | Result |
|---|---|---|---|---|
| TEST-SOAK-001 | Full function, nominal | 72 h | No reset, stable heap, no counter rollover | |
| TEST-ENV-001 | Cold boot at −20 °C (if spec'd) | | | |
| TEST-ENV-002 | Continuous run at +60 °C | | | |

## 6. RF/Wireless (if applicable)
| Test | Method | Pass criteria | Result |
|---|---|---|---|
| PER at deployment range | DTM, 10⁴ packets | ≤1% | |
| RSSI sweep vs. reference | fixed distances/orientations | within 3 dB of reference | |
| Reconnect after edge-of-range | walk test / attenuator | state machine recovery per spec | |

## 7. Traceability Matrix
| Req ID | Implemented in | Verified by | Status |
|---|---|---|---|

## 8. Known Issues and Residual Risks
Every open defect, every FMEA residual RPN, and why each is acceptable for release.


---
