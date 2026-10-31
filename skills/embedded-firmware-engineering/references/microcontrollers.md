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
