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
