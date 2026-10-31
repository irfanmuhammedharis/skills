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
