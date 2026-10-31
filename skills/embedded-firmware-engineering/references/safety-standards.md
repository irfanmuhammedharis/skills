# Safety Standards and Certification Awareness for Firmware

## Contents
1. When standards apply
2. IEC 60730 Class B (appliances) — the most common
3. IEC 61508 / functional safety basics
4. MISRA C practical adoption
5. Certification pathway and documentation
6. Domain quick map

---

## 1. When Standards Apply

- The product controls something that can hurt people or property (heaters, motors, mains, medical, automotive) → safety analysis is mandatory thinking even if formal certification isn't.
- Certification is a market decision: household appliances (IEC 60730), industrial (IEC 61508), automotive (ISO 26262), medical (IEC 62304), rail (EN 50128). Determine at Gate 0 — retrofitting safety is 10× the cost.
- Even without formal certification, apply the engineering practices: single-fault tolerance, self-tests, defensive monitoring. This file gives awareness-level guidance; formal certification requires notified bodies and licensed tools — say so when the user's project is headed there.

## 2. IEC 60730 Class B (appliances) — the Most Common

Class B = software intended to prevent hazards in appliances. Firmware requirements (self-tests run periodically, typically at startup and/or during operation):
- **CPU registers test**: stuck-at test of registers.
- **Program counter test**: watchdog + logical program-flow monitoring.
- **Interrupt handling test**: verify interrupts fire at expected rates (counter cross-check).
- **Clock test**: independent reference comparison (e.g., LSI vs. HSE ratio check on STM32).
- **Flash integrity**: CRC over code memory, periodic or at boot.
- **RAM test**: March pattern or checkerboard, non-destructive during operation (test in slices) or full at boot.
- **Stack test**: overflow detection (guard patterns).
- **Peripheral tests**: ADC plausibility (known reference channel), GPIO read-back, comms CRC.

Vendor libraries: ST X-CUBE-CLASSB (STM32), certified Class B libraries exist for most major MCUs — use them rather than writing your own; they come with certification evidence. Design consequence: the safe state must be reachable when any self-test fails — the FMEA safe-state table and the Class B failure handler are the same mechanism.

## 3. IEC 61508 / Functional Safety Basics

- SIL 1–4 by risk; firmware contributes via systematic capability: development process rigor, diagnostics (diagnostic coverage % — the fraction of dangerous failures your self-tests catch), and hardware fault tolerance.
- Key firmware patterns: dual-channel/diverse processing for safety functions, monitored watchdogs (windowed, external), safe-state enforcement, proven-in-use or certified components (RTOS, libraries).
- An independent safety channel (the safety function does not depend on the MCU running the main app) is the strongest pattern — often a supervisor IC or second small MCU.
- If the user's product is SIL-rated: state clearly that formal assessment, certified toolchain, and safety lifecycle documentation are required — assist with the engineering, don't imply the skill's output is "certified."

## 4. MISRA C Practical Adoption

- MISRA C:2012 (+AMD) — the de facto safe C subset. Practical adoption tiers:
  - Tier 1 (every project): no undefined behavior enablers — fixed-width types, no out-of-bounds, no unbounded loops without exit proof, switch has default, no dynamic memory misuse.
  - Tier 2 (professional): run a checker (cppcheck `--addon=misra`, PC-lint, Coverity); zero unmitigated violations; deviations documented with rationale in code comments.
  - Tier 3 (certified): full compliance report as certification evidence.
- Pair with CERT C for security-adjacent rules.
- Coding standard beyond MISRA: define and enforce naming (module_prefix_function), one module = one .c/.h, header guards, no globals without justification, const-correctness.

## 5. Certification Pathway and Documentation

Typical flow: hazard analysis → safety requirements (with integrity levels) → architecture meeting them → implementation under controlled process → verification with coverage metrics → assessment/audit. The documentation trail IS the product:
- Requirements traceability (see requirements-fmea.md) — certification auditors live in this matrix.
- FMEA/FMEDA (add diagnostic coverage numbers).
- Test plans with evidence; tool qualification records; configuration management (every binary traceable to sources).
- EMC and radio certifications (CE/FCC) run in parallel — see antenna-rf.md §6.
Budget reality: certification adds months and 5–6 figures; flag it in project estimates.

## 6. Domain Quick Map

| Product | Standards to check |
|---|---|
| Home appliance (heater, motor, mains) | IEC 60730 Class B, IEC 60335 |
| Industrial controller | IEC 61508, IEC 61131 (PLC) |
| Medical device | IEC 62304 (software lifecycle), ISO 14971 (risk), IEC 60601 (hardware) |
| Automotive | ISO 26262 (ASIL), AUTOSAR, MISRA mandatory |
| Battery-powered consumer | UN 38.3 (battery transport), IEC 62133 (battery safety) |
| Radio device | FCC/CE-RED, plus duty-cycle firmware rules (see antenna-rf.md) |
| Smart meter/utility | IEC 62052/62053, DLMS/COSEM |

State the applicable set at Gate 0; if unsure, list candidates and tell the user what to confirm with their compliance contact.
