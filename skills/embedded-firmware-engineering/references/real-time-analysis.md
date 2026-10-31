# Real-Time Analysis: Schedulability, Latency, and Resource Budgets

## Contents
1. Timing requirement capture
2. Rate Monotonic Analysis (RMA) — the math
3. Interrupt latency budgeting
4. WCET estimation and measurement
5. Priority inversion and its cures
6. Memory budgeting methodology

---

## 1. Timing Requirement Capture

Build the timing table at Gate 1 — every periodic activity:

| Task/ISR | Period | Deadline | Est. WCET | Priority | Justification |
|---|---|---|---|---|---|
| radio_isr | event, ≤2 ms bursts | 500 µs | 80 µs | highest | RX FIFO overflow at 1 Mbps |
| motor_ctl | 1 ms | 1 ms | 120 µs | high | current loop stability |
| sensor_poll | 100 ms | 50 ms | 2 ms | medium | filter Nyquist |
| telemetry | 60 s | 5 s | 400 ms | low | cloud contract |

A deadline without a measured worst case is a guess. Schedule this table, then verify on hardware (§4).

## 2. Rate Monotonic Analysis (RMA) — the Math

- Assign priorities: shortest period = highest priority (rate-monotonic). For fixed-priority preemptive scheduling this is optimal.
- Utilization bound (Liu & Layland): U = Σ(Ci/Ti) ≤ n(2^(1/n) − 1) ≈ 0.69 for large n. **Keep total CPU utilization ≤0.7** for comfort margin; above it, do exact response-time analysis.
- Exact response-time test (per task i): iterate R = Ci + Σ_ceil(R/Tj)·Cj over higher-priority j until stable; require R ≤ deadline.
- Include ISRs as highest-priority "tasks" in the utilization sum — they consume CPU too.
- Blocking term B (worst time a lower-priority task holds a needed resource) adds to every response time: R = Ci + Bi + Σ…. Keep critical sections microseconds-short.
- Show this calculation in the architecture document for any system with ≥3 concurrent timing activities.

## 3. Interrupt Latency Budgeting

Total latency = hardware entry (~12 cycles Cortex-M) + max interrupt-disabled section + higher-priority ISR execution + (RTOS: critical sections). Measure the worst interrupt-disabled span:
- Audit every `__disable_irq()`, RTOS critical section, and driver lock; time them (cycle counter / scope on a GPIO).
- Budget example: radio needs ≤500 µs service; worst disabled span 40 µs + worst higher ISR 60 µs → margin 5×. State it.
- Cortex-M tail-chaining and late-arrival reduce real latency; a bad NVIC priority assignment destroys it — assign priorities deliberately (radio > motor > comms > housekeeping).

## 4. WCET Estimation and Measurement

- Estimation: count instructions on the worst path with caches/flash-wait-states considered (XIP flash and cache misses inflate 10–50× — measure instead).
- Measurement (do this, always): DWT cycle counter (CYCCNT) around the code, or GPIO toggle + oscilloscope/logic analyzer. Run the worst-case stimulus (max payload, worst branch, flash erase concurrent), record max over ≥10⁴ runs.
- Report WCET as measured-max × 1.5 safety factor, and put the number in the timing table.
- Beware "usually fast" traps: malloc, printf, floating point, string ops, flash writes, TLS handshakes — all have long tails.

## 5. Priority Inversion and Its Cures

- Scenario: low task holds mutex; medium task preempts; high task blocked on mutex → high effectively runs at medium priority.
- Cures: priority inheritance mutexes (FreeRTOS `xSemaphoreCreateMutex` has it — plain binary semaphores do NOT; Zephyr mutexes do); keep critical sections short; prefer lock-free single-writer queues; never take a mutex in an ISR.
- Deadlock audit: document lock ordering; a mutex taken in two different orders across the codebase is a time bomb.

## 6. Memory Budgeting Methodology

At Gate 1, produce and track:

| Resource | Budget | Method to verify |
|---|---|---|
| Flash | app ≤60% of slot (OTA headroom) | linker map file per build; CI check |
| Static RAM (.data+.bss) | ≤50% | map file |
| Stacks | measured watermark +30% | `uxTaskGetStackHighWaterMark` after soak |
| Heap | high-water +30%, or zero (static only) | `xPortGetMinimumEverFreeHeapSize` / mallinfo |
| Retained/no-init | explicit region | linker script review |

- Read the map file on every release build — sudden growth = scope creep or accidental debug code.
- Stack sizing is measured, never guessed: watermark after a soak covering worst-case call depth (deepest: fault handler during printf during TLS).
- Flash wear budget: writes/day × expected life years × cycles-per-write vs. flash endurance (typ. 10k–100k); add wear-leveling factor. Show the math for any device writing logs/config daily.
