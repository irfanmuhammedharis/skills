---
name: embedded-firmware-engineering
description: "Expert-grade embedded systems engineering for production and industrial devices: firmware, circuit design, PCB layout. Also fires on a vague hardware/IoT product idea with no chip or protocol picked yet, not only when a part number is already named. Use for firmware in Embedded C, Arduino C++, or MicroPython on STM32, ESP32/S3/C3, nRF52/53/91, RP2040/2350 Pico, Linux SBCs, Arduino; RTOS (FreeRTOS/Zephyr); toolchains (PlatformIO, CubeIDE, nRF Connect, GCC/Keil/IAR, debug probes, CI/CD); hardware design (power, protection, analog front-ends, PCB/DFM); industrial (24V I/O, 4-20mA, isolation, EMC immunity, Modbus/CANopen/EtherCAT/PROFINET/IO-Link/OPC UA, RS-485); sensors, actuators, battery, HMI; antenna/RF (BLE, Wi-Fi, LoRa, GNSS, cellular); protocols (UART, I2C, SPI, CAN, MQTT, LoRaWAN, Zigbee); IoT end-to-end; manufacturing (DFT, ICT/FCT, serialization, obsolescence, RMA); reliability: FMEA, real-time analysis, watchdogs, OTA, secure boot, IEC 62443, HIL testing, safety standards, pre-production checks."
---

# Embedded Firmware Engineering

Produce production-grade firmware that survives real-world conditions — not demo code. Operate as an elite embedded engineer: every claim is quantified, every failure mode is analyzed before it happens in the field, and every deliverable carries evidence.

## The Gated Workflow

Work through gates in order. Each gate has mandatory artifacts — do not produce Gate 2 code without Gate 1 artifacts. For small tasks, compress the gates but never skip the thinking: state the assumptions, the failure modes, and the verification for whatever you produce.

### Gate 0 — Concept and Requirements

- Capture requirements with IDs (`REQ-FUN-001`, `REQ-PWR-001`, `REQ-ENV-001`): function, power, environment, timing, interfaces, failure consequences
- State every assumption explicitly when the user is vague
- Deliverable: requirements list from [assets/templates/firmware-spec-template.md](assets/templates/firmware-spec-template.md) §1–2
- **Read**: [references/requirements-fmea.md](references/requirements-fmea.md)

### Gate 1 — Architecture and Risk Analysis

- Execution model (super-loop / RTOS / event-driven) with justification; layered architecture; state machines for system and every peripheral
- **FMEA table** (mandatory for anything beyond a toy): every component × failure mode × detection × response — from [assets/templates/fmea-worksheet.md](assets/templates/fmea-worksheet.md)
- Memory map and budgets: Flash/RAM with ≥20% headroom; power budget table with calculated battery life
- Timing architecture: task/interrupt list with periods, priorities, deadlines; run schedulability check
- Interface contracts: ICD for every bus/protocol from [assets/templates/interface-control-document.md](assets/templates/interface-control-document.md)
- **Read**: [references/real-time-analysis.md](references/real-time-analysis.md), [references/microcontrollers.md](references/microcontrollers.md), plus the MCU platform file (table below)

### Gate 2 — Implementation

- Follow the coding standard and non-negotiable rules below
- Every register config cites the datasheet; every timing claim shows the math
- Use the calculator for recurring math instead of hand-computing: `python3 scripts/embedded_calc.py <link-budget|i2c-pullup|baud-error|battery-life|crc16> ...`
- **Read**: the MCU platform file + relevant domain files (tables below)

### Gate 3 — Verification

- Test plan from [assets/templates/test-plan-template.md](assets/templates/test-plan-template.md): unit (host), HIL, fault injection, soak, resource measurements
- Traceability matrix: every REQ-* maps to code and to a test; nothing untested ships
- **Read**: [references/reliability-testing.md](references/reliability-testing.md), [references/debugging-methodology.md](references/debugging-methodology.md)

### Gate 4 — Production Readiness

- Pre-production checklist (evidence required per item) — [references/reliability-testing.md](references/reliability-testing.md) §6
- Manufacturing/provisioning runbook; OTA rollback verified; debug ports locked
- **Read**: [references/iot-firmware.md](references/iot-firmware.md) §7, [references/safety-standards.md](references/safety-standards.md) if the product has safety or certification exposure

## Non-Negotiable Implementation Rules

- Every interrupt has a latency budget; ISRs do no work beyond flag-setting or queue push
- Every blocking call has a timeout; every external input is validated; every stored datum has a CRC
- Watchdog enabled from day one, refreshed only by a health supervisor after all subsystems check in
- Every flash write is power-fail safe; brown-out detection configured; reset cause logged at boot
- Fixed-width types; volatile + critical sections for shared data; no dynamic allocation after init
- No magic numbers; `-Wall -Wextra -Werror` clean; static analysis clean
- Safe-state defined for every output (relays, motors, heaters) on any fault

## Reference Files

Load the MCU platform file for the target chip **plus** the domain files the task touches. Files are one level deep — read them directly.

### MCU platform files

| Platform | Reference file |
|---|---|
| Arduino (AVR, SAMD, STM32duino, nRF52/ESP32 Arduino cores) | [references/arduino.md](references/arduino.md) |
| ESP32 / S2 / S3 / C3 / C6 (ESP-IDF and Arduino core) | [references/esp32.md](references/esp32.md) |
| STM32 (F/G/L/H/WB/WL series, HAL/LL, CubeMX) | [references/stm32.md](references/stm32.md) |
| Nordic nRF52 / nRF53 / nRF91 (nRF Connect SDK) | [references/nrf.md](references/nrf.md) |
| Raspberry Pi RP2040/RP2350 (Pico) and Linux SBCs | [references/raspberry-pi.md](references/raspberry-pi.md) |

### Programming language files (load the one matching the implementation language)

| Language | Reference file |
|---|---|
| Embedded C (bare-metal/driver C, types, volatile, fixed-point, linker, UB traps) | [references/embedded-c.md](references/embedded-c.md) |
| MicroPython and Arduino C++ patterns | [references/micropython.md](references/micropython.md) |
| FreeRTOS / Zephyr — task design, primitives, ISR handoff, debugging | [references/rtos.md](references/rtos.md) |

### Process and analysis files

| Domain | Reference file |
|---|---|
| Requirements engineering, traceability, FMEA methodology | [references/requirements-fmea.md](references/requirements-fmea.md) |
| WCET, schedulability (RMA), interrupt latency, memory budgeting | [references/real-time-analysis.md](references/real-time-analysis.md) |
| Schematic/hardware review for firmware engineers | [references/hardware-review.md](references/hardware-review.md) |
| Systematic debugging, race conditions, field returns | [references/debugging-methodology.md](references/debugging-methodology.md) |
| PlatformIO, vendor IDEs, compilers, debug probes, CI/CD, RF test tools | [references/toolchains-platformio.md](references/toolchains-platformio.md) |
| Safety standards (IEC 60730/61508, MISRA), certification path | [references/safety-standards.md](references/safety-standards.md) |

### Hardware domain files

| Domain | Reference file |
|---|---|
| MCU selection, clock/power, peripherals, bootloader, OTA | [references/microcontrollers.md](references/microcontrollers.md) |
| Circuit/schematic design: power supplies, protection, analog front-end, filters, component derating | [references/circuit-design.md](references/circuit-design.md) |
| PCB layout: stackup, grounding, decoupling, mixed-signal, thermal, DFM | [references/pcb-layout.md](references/pcb-layout.md) |
| Sensor selection, interfacing, calibration, filtering, failure modes | [references/sensors.md](references/sensors.md) |
| Motors, relays, displays/HMI, battery charging and fuel gauges | [references/actuators-power-hmi.md](references/actuators-power-hmi.md) |
| UART/I2C/SPI/CAN/Modbus/USB + BLE/Wi-Fi/LoRa/Zigbee/MQTT stacks | [references/communication-protocols.md](references/communication-protocols.md) |
| Industrial protocols: Modbus deep, CANopen, EtherCAT, PROFINET, EtherNet/IP, IO-Link, OPC UA, Sparkplug, RS-485 networks, PTP | [references/industrial-protocols.md](references/industrial-protocols.md) |
| Industrial electrical design: 24 V systems, IEC 61131-2 I/O, 4–20 mA, isolation, IEC 61000-4-x EMC immunity, environmental hardening | [references/industrial-design.md](references/industrial-design.md) |
| Antenna selection, matching, PCB layout, regulatory, link budget | [references/antenna-rf.md](references/antenna-rf.md) |
| IoT architecture, cloud provisioning, device lifecycle | [references/iot-firmware.md](references/iot-firmware.md) |
| Crypto, secure elements, key storage, secure boot/OTA security, IEC 62443 | [references/firmware-security.md](references/firmware-security.md) |
| Watchdogs, testing, EMI/EMC, pre-production checklists | [references/reliability-testing.md](references/reliability-testing.md) |
| Manufacturing: DFT, ICT/FCT fixtures, serialization/calibration traceability, obsolescence, lifecycle maintenance, RMA | [references/manufacturing-lifecycle.md](references/manufacturing-lifecycle.md) |

## Bundled Tools

- `scripts/embedded_calc.py` — verified calculators: RF link budget, I2C pull-up sizing, UART baud error, battery life from a power budget, CRC16. Use it and paste results (with inputs) into documentation.
- `assets/templates/` — copy and fill: firmware-spec-template.md, interface-control-document.md, test-plan-template.md, fmea-worksheet.md.

## Output Quality Bar

- Numbers over adjectives: "current: 4.2 µA sleep, 240 ms wake latency, 11 dB link margin" — never "low power, fast, good range"
- Every table of requirements, every FMEA row, every test case has an ID and cross-references
- When uncertain about a part-specific detail (register bit, errata), state the uncertainty and name the datasheet/section to verify — never invent values
- If the user's design has a flaw (undersized PSU, missing termination, unsafe default state), say so directly, quantify it, and propose the fix
