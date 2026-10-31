# Reliability, Testing, and Pre-Production Verification

## Contents
1. Watchdog and fault handling
2. Defensive coding standards
3. Test strategy (unit → HIL → fault injection)
4. EMI/EMC hardening
5. Environmental and power testing
6. Pre-production checklist

---

## 1. Watchdog and Fault Handling

- Window watchdog preferred over simple watchdog; refresh only from a dedicated supervisor after every subsystem reports healthy (heartbeat flags from each task/ISR domain).
- On watchdog reset: preserve RAM diagnostics (no-init section), log reset cause + last heartbeat states, then enter degraded-safe mode if the fault repeats (N consecutive watchdog resets → safe state, alert, wait for recovery command).
- Hard fault handler: capture stacked registers (PC, LR, xPSR, fault status/address registers like CFSR/HFSR/BFAR on Cortex-M), store to flash/no-init RAM, then reset. A device that silently reboots is undebuggable in the field.
- Assert policy: debug build = trap + breakpoint; release build = log + controlled recovery. Never ship handlers that just `while(1)`.
- Define safe-state for the product: what do outputs (relays, motors, heaters, valves) do on any fault? Default must be the fail-safe direction.

## 2. Defensive Coding Standards

- Compiler: `-Wall -Wextra -Werror`; add `-Wshadow -Wconversion` for new code. MISRA-C:2012 subset for safety-relevant C; run a static analyzer (PC-lint, clang-tidy, cppcheck) — zero warnings policy.
- No dynamic allocation after init in long-running devices (fragmentation); use static/pool allocation.
- Check every return value; mark intentional ignores explicitly.
- Integer discipline: fixed-width types, explicit signedness, overflow-checked arithmetic for time (handle tick wraparound — `if ((int32_t)(now - deadline) >= 0)` pattern).
- Shared data: volatile + critical sections or lock-free single-writer patterns; document every ISR/task shared variable.
- Version everything: firmware semantic version, build hash, hardware revision — readable via debug interface and reported to cloud.

## 3. Test Strategy

### Unit tests (host-compiled)
- All pure logic (parsers, filters, state machines, CRC, protocol framing) compiles and runs on the host with a framework (Unity, CppUTest, Google Test). Target ≥80% coverage on logic modules.
- State machines get transition-table-driven tests: every state × every event, including illegal ones.

### Hardware-in-the-loop
- Driver tests on real hardware: sensor present/absent, boundary reads, timing verification.
- Automated: script-driven flashing + UART-output assertion, run per commit.

### Fault injection (mandatory before "flawless" claims)
Run and document results for:
- Unplug each sensor mid-operation → system detects, degrades, recovers on replug
- Corrupt packets (bit flips, truncation, replay) → CRC rejects, counters increment, no crash
- Kill power during flash write / OTA swap at random points ×20 → device always boots a valid image, config never corrupt
- Brown-out sweep (variable PSU, slow ramp 0→VDD) → BOR holds reset until valid voltage, no runaway
- I2C bus held low (slave fault simulation) → recovery sequence restores bus
- Wi-Fi/broker outage 24–72 h → buffering, backoff, recovery without reboot loop
- 72 h+ soak test at full functionality → no memory leak (heap watermark stable), no counter rollover, no drift
- Temperature extremes (if spec'd): cold boot at min temp, continuous run at max temp

### Timing/resource verification
- Measure: worst-case ISR latency, task stack watermarks (all tasks ≥30% free), heap high-water, boot time, sleep current, radio TX current. Compare against budget table — every number documented.

## 4. EMI/EMC Hardening (Firmware + Hardware Co-Design)

- Firmware measures that survive ESD/EFT events: watchdog (always), periodic re-init of critical peripherals (I2C/SPI peripherals lock up after transients), RAM scrubbing or periodic re-verification of critical config (SEU resilience).
- External watchdog / supervisor IC for anything controlling hazardous loads.
- Debounce all external inputs in firmware (buttons, interrupt lines) — ESD on cables causes phantom interrupts; count and rate-limit interrupt storms.
- Unused interrupt vectors point to a handler that logs and returns — never default to hanging.
- Hardware: ESD diodes on external connectors, common-mode chokes on wired buses leaving the board, series resistors on long GPIO runs.

## 5. Environmental and Power Testing

- Power: test with the actual battery/PSU, including weak battery (internal resistance rises → voltage sags on TX bursts → spurious resets; add bulk capacitance or reduce TX power at low battery).
- Mains-powered: test with relay/motor loads switching nearby — conducted transients are the classic field failure.
- RF devices: test at the edge of coverage, during hand/body proximity, inside the final enclosure (see antenna-rf.md §7).
- Thermal: verify no component exceeds rating at max ambient + full load; firmware should implement thermal derating where relevant (reduce TX power, throttle sampling).

## 6. Pre-Production Checklist

Apply before declaring any firmware production-ready. Every item must have evidence (test log, measurement, or code reference):

**Boot & Recovery**
- [ ] Reset cause logged and recoverable from field devices
- [ ] Watchdog active, refresh policy documented, fault-escalation path tested
- [ ] Hard fault handler captures context to persistent storage
- [ ] OTA rollback verified with power cuts at every phase

**Code Quality**
- [ ] Zero compiler warnings at `-Wall -Wextra -Werror`
- [ ] Static analysis clean (or every warning justified in writing)
- [ ] No magic numbers; every register config cites datasheet
- [ ] Version/build info embedded and readable

**Resources**
- [ ] Stack watermarks ≥30% free on all tasks (measured, soak-tested)
- [ ] Heap high-water documented; no leaks over 72 h soak
- [ ] Flash/RAM headroom ≥20%
- [ ] ISR latency measured within budget

**Peripherals & Sensors**
- [ ] Every external input range-checked
- [ ] Every blocking operation has a timeout
- [ ] Sensor fault detection + recovery tested per sensor
- [ ] Calibration stored with CRC + factory fallback

**Communications**
- [ ] CRC/framing validation on every protocol
- [ ] Reconnect/backoff state machines tested with real outages
- [ ] Offline buffering behavior verified (capacity, eviction, catch-up)

**Power & Environment**
- [ ] Current budget measured and matches calculation in all modes
- [ ] Brown-out tested with slow voltage ramps
- [ ] Sleep current measured (not calculated) on final hardware
- [ ] Operation verified at temperature extremes if spec'd

**Security & Production**
- [ ] Debug ports locked in production build
- [ ] No shared fleet credentials; secure storage for keys
- [ ] Signed OTA enforced; unsigned image rejected (tested)
- [ ] End-of-line production test defined and documented
