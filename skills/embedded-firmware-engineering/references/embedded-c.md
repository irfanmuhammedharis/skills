# Embedded C: Production Language Discipline

## Contents
1. Type and arithmetic discipline
2. volatile, atomics, and shared data
3. Register and bit manipulation patterns
4. Fixed-point math
5. Memory: sections, linker, startup
6. Driver architecture in C
7. Undefined behavior traps
8. Host-based unit testing of C

---

## 1. Type and Arithmetic Discipline

- Always fixed-width: `uint8_t/uint16_t/uint32_t/int32_t` from `<stdint.h>`; `int` is forbidden in portable driver code (width varies).
- Signedness: unsigned for registers/protocols/bitfields; signed only when negatives are real. Never compare signed against unsigned (`-Wsign-compare` must be on).
- Overflow is design input: for every counter, state the wrap time (32-bit ms tick wraps at 49.7 days — handle with subtraction arithmetic: `(int32_t)(now - deadline) >= 0`).
- `size_t` for sizes/indices; `ptrdiff_t` for pointer arithmetic; cast deliberately, never implicitly narrow.
- Avoid float on MCUs without FPU (10–100× slower, pulls in big libraries). If FPU exists, verify ISR context saving cost before using float in interrupts.

## 2. volatile, atomics, and Shared Data

- `volatile` means "this can change outside the compiler's view" — required for: ISR-shared variables, MMIO registers, variables touched by DMA buffers. It is NOT a synchronization primitive.
- Shared-data rules:
  - Single-byte flag ISR→task: `volatile` + clear-after-read is acceptable.
  - Multi-byte data ISR→task: critical section (disable IRQ / RTOS taskENTER_CRITICAL) around read, or lock-free single-writer circular buffer.
  - Multi-producer: use an RTOS queue — hand-rolled multi-producer lock-free code is a PhD thesis, don't.
- Compiler barriers: `__DMB()`/memory clobber when ordering matters (DMA descriptor setup before enabling DMA).
- Audit pattern: grep `volatile` — every instance must have a comment naming its writer contexts.

## 3. Register and Bit Manipulation Patterns

- Read-modify-write with masks; never magic numbers:
```c
#define ADC_CR1_RES_Pos      (24U)
#define ADC_CR1_RES_Msk      (0x3U << ADC_CR1_RES_Pos)
reg = (reg & ~ADC_CR1_RES_Msk) | (0x2U << ADC_CR1_RES_Pos);
```
- CMSIS headers on Cortex-M — use vendor SVD-derived headers, not hand-written addresses.
- Struct overlays on registers: legal only with exact packing + volatile members; prefer CMSIS-style definitions.
- Bit-banding/bit-fields: avoid for portable code; avoid C bit-fields for hardware registers (layout is implementation-defined — the standard trap).
- Every register write in driver init: comment with datasheet reference ("RM0390 §13.4.2: enable dual regular simultaneous mode").

## 4. Fixed-Point Math

- Represent quantities in scaled integers: millivolts, centi-degrees, Q15/Q31 for DSP. Document the scale at the type: `typedef int32_t millivolt_t;`
- Q-format arithmetic: Q15 multiply = `(a*b)>>15` with int32 intermediate; watch overflow — saturate deliberately (`__SSAT` on Cortex-M or explicit clamp).
- Division: precompute reciprocals as shifts where the divisor is constant; avoid 64-bit division on M0 (pulls big library).
- Filters in fixed point: state and coefficients in wider type; verify no overflow at worst-case input (show the analysis).

## 5. Memory: Sections, Linker, Startup

- Know your linker script: `.text .rodata .data .bss .stack .heap`, plus custom: `.noinit` (survives reset — black-box data), `.ccmram`, `.ramfunc` (code from RAM for flash-write-time execution).
- Startup code: vector table → copy .data flash→RAM → zero .bss → call static constructors (C++) → main. Bootloader-left state must be de-initialized before this (clocks, DMA, interrupts).
- No-init section usage pattern: magic word + CRC validates contents after watchdog reset; discard on cold boot.
- Stack: single main stack + ISR stack model vs. per-task RTOS stacks; size from measurement (reliability-testing.md), guard via MPU or fill-pattern check.
- Heap policy: none in long-running devices (fragmentation is a slow DoS); static pools with block sizes per use case when needed; `malloc` in init-only paths is acceptable with justification.

## 6. Driver Architecture in C

- One module = one `drv_xxx.c/h`; header exposes only opaque handle + init/config/process API; state in a struct, not globals (multi-instance ready).
- Layering enforced by include discipline: application includes driver headers; drivers never include application headers.
- Every driver: `init()` returns status, `deinit()` for power management, `self_test()` where hardware supports it, error enum shared project-wide.
- Non-blocking pattern: `start()` → interrupt/DMA → callback/flag → `result()`. Blocking variants exist only as wrappers with timeout for init-time use.
- Config via struct passed to init (baud, pins abstracted as instance data) — no `#define`-configured drivers in reusable code.
- Defensive ABI: validate pointers/ranges at API boundary, not at every internal call.

## 7. Undefined Behavior Traps

- Shift by ≥ width or negative: UB — mask and range-check shift amounts.
- Signed integer overflow: UB (not wrap!) — use unsigned for wrap-around semantics.
- Strict aliasing: no type-punning through pointers (use `memcpy` or unions); compile `-fno-strict-aliasing` if legacy code demands it — document why.
- Uninitialized reads, out-of-bounds, use-after-free: enabled sanitizers in host tests (ASan/UBSan) catch these before hardware does.
- `assert()` compiled out in release: never put side effects in assert expressions.

## 8. Host-Based Unit Testing of C

- Architecture payoff: pure logic (parsers, filters, state machines, CRC, schedulers) compiles for the host — hardware access behind a HAL interface mocked in tests.
- Framework: Unity/CMock or CppUTest; run with `gcc -fsanitize=address,undefined -Wall -Wextra -Werror`.
- State machines: transition-table tests (every state × every event including illegal).
- Parsers: fuzz lightly — random + mutated inputs for ≥10⁵ iterations under ASan/UBSan.
- This is the CI layer from toolchains-platformio.md §5; a firmware project without host tests is a prototype.
