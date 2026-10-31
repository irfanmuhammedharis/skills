# Requirements Engineering and FMEA for Firmware

## Contents
1. Writing testable requirements
2. Requirement ID system and traceability
3. FMEA methodology (the core elite practice)
4. Fault trees and hazard analysis
5. Common requirement mistakes

---

## 1. Writing Testable Requirements

A requirement is only valid if a test can prove or disprove it. Transform vague statements:

| Vague | Testable requirement |
|---|---|
| "low power" | REQ-PWR-003: Average current ≤15 µA over a 10-min reporting cycle, measured at 3.6 V, 25 °C |
| "fast response" | REQ-TIM-001: Button press to actuator output ≤50 ms, 99th percentile, over 1000 trials |
| "reliable connection" | REQ-COM-002: After any network outage ≤72 h, device reconnects within 5 min of restoration and uploads ≥99% of buffered samples |
| "accurate temperature" | REQ-SEN-001: ±0.5 °C over 0–50 °C after 2-point calibration, verified against reference thermometer at 5 points |
| "robust" | REQ-REL-001: Device recovers to full function without manual intervention after any single sensor disconnect/reconnect |

Every requirement needs: ID, statement with number + condition + tolerance, priority (MoSCoW), verification method (test/analysis/inspection/demonstration), and source (user request/assumption/derived).

## 2. Requirement ID System and Traceability

- Prefixes: `REQ-FUN` (function), `REQ-TIM` (timing), `REQ-PWR` (power), `REQ-ENV` (environment), `REQ-COM` (communications), `REQ-REL` (reliability), `REQ-SEC` (security), `REQ-SAF` (safety), `REQ-MFG` (manufacturing).
- Traceability matrix (keep in the spec, update every gate):

| Req ID | Implemented in | Verified by | Status |
|---|---|---|---|
| REQ-PWR-003 | power.c:enter_sleep() | TEST-PWR-101 (PPK2 measurement) | PASS 2024-… |

- A requirement without a test is a wish. A test without a requirement is scope creep. Match them both ways.
- Changes: requirement changes get versioned with rationale; re-run affected tests (the matrix tells you which).

## 3. FMEA Methodology (the core elite practice)

For every component/function, enumerate failure modes systematically. Severity (S), Occurrence (O), Detection (D) on 1–5; RPN = S×O×D; attack highest RPN first.

| ID | Item | Failure mode | Effect | S | O | D | RPN | Mitigation (detection → response) |
|---|---|---|---|---|---|---|---|---|
| FM-001 | Temp sensor | Open circuit | Reads full-scale | 3 | 2 | 1 | 6 | Range-check → mark invalid, use last-good ≤5 min, then degrade to safe-state |
| FM-002 | I2C bus | SDA stuck low | All bus devices dead | 4 | 2 | 3 | 24 | Bus-hang detect (timeout) → SCL pulse recovery → power-cycle sensor rail → system reset as last resort |
| FM-003 | Flash | Power cut during config write | Corrupt config | 4 | 3 | 1 | 12 | Double-buffer + CRC → revert to last-good copy, log event |
| FM-004 | Wi-Fi | Outage 72 h | Data loss | 3 | 3 | 1 | 9 | Ring buffer sized for 96 h → oldest-first eviction only at overflow |
| FM-005 | Relay output | MCU hangs with output ON | Heater stuck on | 5 | 2 | 2 | 20 | External watchdog + hardware failsafe (relay defaults OFF on reset; gate drive requires periodic refresh pulse) |
| FM-006 | Battery | Deep discharge | Device unrecoverable in field | 4 | 2 | 2 | 16 | Fuel gauge + low-battery cutoff at 3.0 V, ship-mode below threshold |

Rules:
- Include software failure modes (stack overflow, priority inversion, counter rollover at 49.7 days, buffer full) — not just hardware.
- Include the failure mode "works perfectly but with wrong data" (miscalibration, swapped sensor channels) — the most dangerous class, because nothing looks broken.
- For every S≥4, mitigation must be **hardware or independent-path** — the same MCU that failed cannot be its own only safeguard.
- After mitigation, re-score: document residual RPN and why it's acceptable.
- The FMEA directly generates: the graceful-degradation table, the fault-injection test list, and the watchdog supervision list. If it doesn't, you did it as paperwork — redo it.

## 4. Fault Trees and Hazard Analysis

For top-level hazards ("device causes overheating", "device loses all data"), build a fault tree downward: hazard ← OR/AND gates ← contributing faults. Use it to find single points of failure: any fault that alone reaches the top event through an OR gate is a design liability — eliminate or add an independent barrier.

## 5. Common Requirement Mistakes

- Specifying implementation instead of behavior ("use FreeRTOS" vs. "meet these deadlines") — constrain implementation only when there's a real reason (team skill, certification, existing IP).
- Missing negative requirements: what the device must NOT do (never actuate during OTA, never log PII, never draw >1 mA in ship mode).
- Missing operational envelope: temperature, supply voltage, vibration, humidity — and behavior outside it (must fail safely, not silently).
- Unbounded requirements ("always", "never", "100%") — bound everything ("≥99% over 10⁴ operations").
- Forgetting lifecycle requirements: manufacturability, calibratability, updatability, diagnosability, decommissioning.
