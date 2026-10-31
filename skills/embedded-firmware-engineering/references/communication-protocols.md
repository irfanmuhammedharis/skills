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
