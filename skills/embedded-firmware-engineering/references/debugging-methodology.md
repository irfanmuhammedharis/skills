# Systematic Debugging Methodology for Embedded Systems

## Contents
1. The disciplined process
2. Bug class playbook
3. Race conditions and Heisenbugs
4. Post-mortem from reset/fault data
5. Field returns and fleet debugging
6. Instrumentation that doesn't change behavior

---

## 1. The Disciplined Process

1. **Reproduce deterministically first.** Write down exact steps/conditions/stimulus. A bug you can't reproduce is a bug you can't verify fixed. If intermittent: build a harness that triggers it automatically (loop the operation, log until failure).
2. **Stabilize the observation.** Get visibility before changing anything: logs, scope, debugger. One reliable observation beats ten theories.
3. **Bisect the space.** Hardware vs. software (swap board), code vs. config (revert build), when-introduced (git bisect across commits), which subsystem (disable half). Each experiment must halve the remaining space.
4. **One variable at a time.** Change one thing, observe, record. Shotgun changes create fixes you don't understand — which return.
5. **Prove the fix.** Re-run the reproduction harness N× the failure frequency (failed 1/hour → run 24 h clean minimum), then add a regression test so it can never come back silently.
6. **Write the post-mortem**: symptom → root cause → fix → prevention. Root cause means "why did the process let this through," not just the line of code.

## 2. Bug Class Playbook

| Symptom | Most likely causes (check in order) |
|---|---|
| Random resets | Watchdog (which task starved?) → brown-out (scope the rail during radio TX) → stack overflow (watermarks) → hard fault (read CFSR/BFAR) |
| Works on bench, fails in field | Temperature (crystal drift, battery voltage drop) → power quality → RF environment → uninitialized state only exercised by field sequence |
| Dead after days/weeks | Counter rollover (millis 49.7 d, tick wrap) → memory leak/fragmentation → flash wear → resource leak (sockets, mutexes) → RTC drift |
| Hangs at boot sometimes | Power sequencing/ramp → crystal startup margin → peripheral left running by bootloader → race between init order |
| Data corrupts rarely | ISR/task shared data without protection → DMA + cache coherency (M7) → buffer overrun → flash write during operation |
| I2C/SPI device stops responding | Bus lockup (recovery sequence?) → sensor brown-out (switchable rail?) → NACK storm after ESD |
| Works with debugger attached, fails standalone | Timing dependency (semihosting delay) → uninitialized variable (debug zeroes memory) → watchdog disabled in debug builds |

## 3. Race Conditions and Heisenbugs

- Detection: they move when you add logging. Counter-instrument instead: count events, queue depths, ISR/task interleavings; dump counters periodically — logging changes timing, counters barely do.
- Reproduce by stress: maximize preemption (high-rate timers, artificial load tasks, loopback traffic at max rate); races appear under load, not on the bench.
- Audit pattern: list every shared variable; for each, identify writers and readers (task/ISR context); verify protection. Grep for `volatile`, every one must justify itself.
- Common races: ISR sets flag, task clears after processing but ISR fires between (use atomic swap/queue); multi-byte value torn by ISR mid-read (critical section or atomic snapshot); check-then-act on shared state.
- Priority inversion symptoms: high-priority task occasionally misses deadline while a low-priority task runs — check mutex usage (see real-time-analysis.md §5).

## 4. Post-Mortem from Reset/Fault Data

Mandatory infrastructure (build it before you need it):
- Reset-cause register read + persisted at boot.
- HardFault handler capturing: stacked PC/LR/xPSR, CFSR/HFSR/BFAR/MMAR (Cortex-M), task name, heap/stack watermarks — stored to flash or no-init RAM, retrievable via debug UART and uploaded to cloud.
- Decode: BFAR valid → bus fault at that address (often null/wild pointer); usage fault UNDEFINSTR → corrupted PC (stack smash); IMPRECISERR → enable write-buffer disable or narrow by disabling instructions until precise.
- Keep a ring buffer of last N events (boots, faults, assert codes, resets) in retained RAM — the "black box" that survives the crash.

## 5. Field Returns and Fleet Debugging

- Every field unit must be diagnosable without opening it: version, uptime, reset count by cause, fault counters, last crash dump — queryable over its normal comms channel.
- Fleet telemetry: track reset rate per firmware version per cohort — a 0.5%/day reset rate is invisible on the bench and catastrophic at 10k units.
- Returned units: never reflash before extracting the black-box data and config — the evidence is the product of the return.
- Correlate with environment: batch/date codes, temperature, supply, installation site — field failures cluster by conditions, not randomly.

## 6. Instrumentation That Doesn't Change Behavior

- Prefer: GPIO pulse + logic analyzer (sub-µs cost), DWT cycle counters, event counters, RTT (J-Link, fast and buffered) over UART printf (slow, blocking, changes timing).
- Trace tools: Segger SystemView (RTOS event timeline), Percepio Tracealyzer — see actual task/ISR scheduling vs. intended design.
- Compile-time instrumentation levels: keep the hooks in production (compiled out by level), so the same binary can be diagnosed.
- Golden rule: if the bug vanishes with instrumentation, the instrumentation is the variable — switch to lower-impact observation, don't declare victory.
