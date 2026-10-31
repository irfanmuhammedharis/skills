# RTOS Deep Reference: FreeRTOS, Zephyr, and Task Design

## Contents
1. Do you need an RTOS? (decision framework)
2. Task design patterns
3. FreeRTOS primitives — correct usage
4. ISR-to-task handoff patterns
5. Zephyr specifics
6. Configuration that matters
7. RTOS debugging playbook
8. Anti-patterns

---

## 1. Do You Need an RTOS? (Decision Framework)

- Super-loop + ISRs when: one timing domain, ≤2 concurrent activities, no network stack, team unfamiliarity is a real risk. Determinism is trivially provable.
- RTOS when: ≥3 concurrent timing domains, network/USB stacks, complex power management, multiple developers. Cost: priority inversion risk, stack management, harder WCET proof.
- Event-driven framework (QP/C, Zephyr SMF, protothreads) when: many states, few threads — concurrency without stack-per-task cost.
- State the choice + justification in the Gate 1 architecture (real-time-analysis.md provides the schedulability math).

## 2. Task Design Patterns

- One task per timing domain, not per feature: `task_sensor` (100 ms), `task_comms` (event-driven), `task_ui` (50 ms), `task_housekeeper` (1 s: watchdog feeding, health checks, stats).
- Task anatomy: init phase → infinite loop blocking on queue/notification/period — never polling with `vTaskDelay(1)`.
- Priority assignment: rate-monotonic within task set (real-time-analysis.md §2); ISRs of course higher than any task; housekeeping lowest above idle.
- Stack sizing: measure watermark after soak, then ×1.3 minimum. Stack overflow = the #1 RTOS field failure — `configCHECK_FOR_STACK_OVERFLOW=2` in debug and first-production.
- Health supervision: each task sets its heartbeat bit each cycle; supervisor feeds the watchdog only when all bits set — a hung task must hang the watchdog, not get fed around.

## 3. FreeRTOS Primitives — Correct Usage

| Primitive | Use for | Traps |
|---|---|---|
| Task notification | ISR→task wake, light signaling (fastest, least RAM) | One pending value per task — not a queue |
| Queue | All multi-byte producer→consumer data | Copy semantics (large structs = slow: queue pointers); full-queue policy must be defined (drop oldest/newest/block-with-timeout) |
| Counting semaphore | Resource pools, ISR event counting | Not for mutual exclusion |
| Binary semaphore | Legacy signaling | Task notification is better in almost every case |
| Mutex | Shared resource exclusion | Has priority inheritance — binary semaphores DON'T (the classic inversion bug); never take in ISR |
| Recursive mutex | Rare — redesign instead | Hides call-structure problems |
| Event groups | Multi-condition sync (bits from several sources) | Bits are not data; consumer must re-read state |
| Stream/message buffers | Byte streams ISR↔task (UART TX/RX) | Single writer/single reader only |
| Software timers | Periodic light duties, timeouts | All timer callbacks share one task — keep callbacks tiny; never block |

- Timeouts everywhere: `xQueueReceive(..., portMAX_DELAY)` only where blocking forever is correct by design; everything else gets a bounded timeout + error path.
- `FromISR` variants in interrupts only; `portYIELD_FROM_ISR()` when a wake occurred.

## 4. ISR-to-Task Handoff Patterns

- Pattern A (data): ISR reads hardware → `xQueueSendFromISR` → task processes. For UART/SPI/ADC-complete.
- Pattern B (event): ISR → `vTaskNotifyGiveFromISR` → task does the hardware read. Lower ISR latency, task bears the register access.
- Pattern C (deferred work): heavy processing → pended function or dedicated high-priority worker task.
- Rule: ISR duration budgeted (real-time-analysis.md §3); DMA does bulk movement; the task owns protocol logic. Never parse protocols, call printf, or allocate in an ISR.

## 5. Zephyr Specifics

- Model: threads + workqueues + kernel objects, configured by Kconfig — hardware by devicetree. Read nrf.md §2 for the config layering.
- Threads: static stacks via `K_THREAD_STACK_DEFINE` + `k_thread_create`, or `K_THREAD_DEFINE`; system workqueue for small deferred jobs (never block it).
- Sync: `k_msgq` (queues), `k_sem`, `k_mutex` (priority inheritance), `k_event`, ring buffers for ISR byte streams; `k_poll` for multi-source waits.
- Power: PM subsystem + device runtime PM — tickless is native; device drivers must implement suspend/resume for real sleep currents.
- Logging: `LOG_INF/ERR` deferred — never `printk` in ISRs (timing) — see nrf.md §7.
- Choose Zephyr when: nRF (native), multi-vendor portability target, rich subsystems needed (USB, BLE host, filesystems, shell). FreeRTOS when: minimal footprint, vendor SDK is FreeRTOS-based (ESP-IDF), team already fluent.

## 6. Configuration That Matters (FreeRTOS)

- `configUSE_PREEMPTION=1`, `configUSE_TIME_SLICING=0` for deterministic systems (same-priority round-robin hides bugs).
- `configMAX_PRIORITIES` small (5–8) — forces deliberate priority economy.
- `configMAX_SYSCALL_INTERRUPT_PRIORITY`: every ISR calling FreeRTOS API at/below it — wrong value = rare corruption (the hardest bug class).
- `configASSERT` enabled in debug: catches API misuse at the call site.
- `configCHECK_FOR_STACK_OVERFLOW=2`, `configUSE_MALLOC_FAILED_HOOK=1`, `configRECORD_STACK_HIGH_ADDRESS=1`.
- Tick rate: 100 Hz is plenty for most (1 kHz burns power and shrinks time-slice granularity benefits); tickless idle for battery.
- Heap scheme: heap_4 (coalescing) if dynamic allocation unavoidable; heap_1 or static-only (`configSUPPORT_STATIC_ALLOCATION`) for long-running products.

## 7. RTOS Debugging Playbook

- Deadlock: dump task states (blocked on what?) via `vTaskList()`/debugger RTOS-aware view (J-Link Ozone, STM32CubeIDE FreeRTOS view); check mutex ordering violations.
- Priority inversion: high task delayed while low runs → find the mutex, confirm inheritance, shorten critical section.
- Stack overflow: watermark audit; enable overflow hook that logs task name.
- Missed deadlines: SystemView/Tracealyzer trace — compare actual schedule vs. the Gate 1 timing table; look for surprise blockers (mutexes, full queues, flash writes).
- CPU load: `vTaskGetRunTimeStats` (needs a fast timer configured); idle-task hook counter as poor-man's load meter.

## 8. Anti-Patterns (Reject in Review)

- Task-per-message-type proliferation (10+ tasks, each with own stack, all mostly idle) — merge into domain tasks.
- Polling loops with `vTaskDelay(1)` instead of blocking on an event.
- printf/UART TX inside mutex held across the whole transfer.
- Queues of large structs (copy cost) — queue pointers to pool buffers instead.
- `portMAX_DELAY` everywhere: no timeouts = undiagnosable hangs.
- FreeRTOS API from ISR without `FromISR`, or from ISRs above `configMAX_SYSCALL_INTERRUPT_PRIORITY`.
- Shared globals "because it's faster than queues" — the audit pattern from embedded-c.md §2 applies.
- Software timers doing real work (they serialize in one task).
- Creating/deleting tasks at runtime in long-running products (fragmentation + error paths) — create all at init.
