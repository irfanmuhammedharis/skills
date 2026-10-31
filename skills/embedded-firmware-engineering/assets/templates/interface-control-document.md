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
