# Firmware Specification — [Product Name]

Version: 0.1 | Date: YYYY-MM-DD | Status: DRAFT
Hardware: [MCU + part number, board rev] | Author: [name]

## 1. Overview
One paragraph: what the device does, for whom, in what environment.

## 2. Requirements
| ID | Requirement (number + condition + tolerance) | Priority | Verification | Source |
|---|---|---|---|---|
| REQ-FUN-001 | | Must | Test TEST-FUN-101 | user |
| REQ-PWR-001 | | Must | Measurement | derived |
| REQ-ENV-001 | Operating −20…+60 °C, fail safely outside | Must | Analysis + test | assumption |

## 3. Architecture
- Execution model: [super-loop / FreeRTOS / Zephyr] — justification:
- Layer diagram: application / services / middleware / HAL / hardware
- Execution contexts: tasks and ISRs with period, deadline, priority, est. WCET (see timing table)
- Schedulability: utilization U = ΣCi/Ti = [x] ≤ 0.7; response-time check for tasks above bound

## 4. State Machines
[System state machine: states, events, transitions, timeouts — diagram or table. One per peripheral where applicable.]

## 5. Memory Map and Budgets
| Region | Address/size | Contents |
|---|---|---|
| Bootloader | | |
| App slot A / B | | |
| Config/calibration (CRC'd, double-buffered) | | |
| Log / crash dump | | |
Budgets: Flash app ≤ [60%] of slot; static RAM ≤ [50%]; stacks measured +30%; flash-wear: [writes/day × years vs. endurance].

## 6. Power Budget
| Mode | Current | Duty | Energy contribution |
|---|---|---|---|
| Sleep | | | |
| Active | | | |
| Radio TX | | | |
Average current: [x] → battery life [y] on [battery] (≥30% margin). Measured values replace estimates after first hardware.

## 7. Interfaces
Reference: ICD document [interface-control-document.md] — buses, protocols, payloads, versions.

## 8. Failure Handling (from FMEA)
| Failure | Detection | Response | Safe state |
|---|---|---|---|
| (summary rows from fmea-worksheet.md, S≥3) | | | |

## 9. Security
Threat model summary: assets / attackers / countermeasures. Secure boot: [yes/no + chain]. Key storage: [secure element / eFuse / flash]. Debug lockdown: [plan].

## 10. Verification Plan
Reference: [test-plan-template.md]. Traceability matrix: REQ → code → test → status.

## 11. Manufacturing and Deployment
Flashing/provisioning procedure; per-device data (serial, keys, calibration); end-of-line test; OTA strategy and rollback; field diagnostics (black-box data retrieval).

## Appendix: Assumptions and Open Questions
Every assumption made without user confirmation, and every open question, listed explicitly.
