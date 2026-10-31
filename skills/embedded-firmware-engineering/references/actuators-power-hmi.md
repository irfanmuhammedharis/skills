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
