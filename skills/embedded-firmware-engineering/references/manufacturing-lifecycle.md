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
