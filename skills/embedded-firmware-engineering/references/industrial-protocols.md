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
