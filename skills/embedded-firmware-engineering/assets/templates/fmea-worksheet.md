# FMEA Worksheet — [Product Name]

Version: 0.1 | Date: YYYY-MM-DD
Scales: S/O/D 1–5 (S: 5 = hazard/data loss, 1 = cosmetic; O: 5 = certain in field, 1 = unlikely; D: 5 = undetectable until effect, 1 = detected immediately). RPN = S×O×D.

## Failure Modes
| FM ID | Item | Failure mode | Cause | Effect | S | O | D | RPN | Detection | Response / mitigation | Residual RPN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FM-001 | | | | | | | | | | | |

## Rules for Completing This Worksheet
- Include software failure modes: stack overflow, priority inversion, counter/tick rollover, heap exhaustion, buffer overflow, race conditions, watchdog starvation, corrupt flash, stale data.
- Include the "wrong data, nothing looks broken" class: miscalibration, swapped channels, unit errors, stale readings displayed as fresh.
- Include operational modes: during OTA, during low battery, during network outage, during sensor warm-up, at temperature extremes.
- S ≥ 4 requires an independent-path mitigation (hardware or separate channel), not just more code on the same MCU.
- Every row generates: one entry in the firmware-spec failure-handling table AND one fault-injection test in the test plan. Cross-reference the IDs.
- After mitigation, re-score O and D → residual RPN; justify every residual RPN ≥ 8 in the test plan's risk section.

## Single Points of Failure (from fault tree)
| Hazard | Faults that alone cause it (OR-gate) | Barrier added |
|---|---|---|
