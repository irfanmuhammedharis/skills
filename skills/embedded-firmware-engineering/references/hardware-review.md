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
