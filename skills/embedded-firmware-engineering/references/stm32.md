# STM32 Family — HAL/LL, CubeMX, and Production Firmware

## Contents
1. Family selection
2. Toolchain: CubeMX / CubeIDE workflow
3. Clock tree and power rules
4. Peripheral traps (the flaws that bite)
5. DMA and interrupt architecture
6. Flash, bootloader, and protection
7. Debugging with SWD

---

## 1. Family Selection

| Series | Core | Focus | Notes |
|---|---|---|---|
| F0/G0 | M0/M0+ | Low cost | G0 is the modern F0 replacement |
| F1 | M3 | Legacy general | Old; many clones (GD32/CH32) differ subtly |
| F4 | M4F | Performance general | Workhorse; F405/F407/F411 common |
| G4 | M4F | Analog/motor | Fast ADCs, op-amps, HRTIM |
| L4/L4+/U5 | M4F/M33 | Low power | U5 adds TrustZone, best-in-class sleep |
| H7 | M7/M4 dual | High performance | Cache coherency complexity — see §5 |
| WB/WBA | M4+M0+ / M33 | BLE | Radio on second core, firmware via FUS — special update flow |
| WL | M4 | Sub-GHz LoRa | Integrated SX126x |
| MP1 | A7+M4 | Linux-capable | Different ecosystem entirely |

Rule: pick the cheapest series that meets ADC/timer/peripheral needs with 2× flash headroom; check the errata sheet for the exact part + silicon revision before design freeze.

## 2. Toolchain: CubeMX / CubeIDE Workflow

- CubeMX generates initialization code + `.ioc` project file. Commit the `.ioc` to version control — it is the hardware configuration of record.
- Generated code has `USER CODE BEGIN/END` sections: **all user code goes inside them** or a CubeMX regeneration silently deletes it. For anything non-trivial, keep CubeMX output as init-only and write drivers separately.
- HAL vs. LL: HAL for speed of development on complex peripherals (USB, ETH, SDMMC); LL or direct register for timing-critical paths (ADC+DMA, timers). Mixing is normal — document where and why.
- CubeIDE = Eclipse + GCC + ST-Link debugger; alternatives: Keil MDK (commercial, strong optimizer), IAR (commercial, safety cert options), plain arm-none-eabi-gcc + CMake (best for CI). See toolchains-platformio.md.
- Pin the CubeMX/HAL firmware-package version per project; HAL upgrades change behavior.

## 3. Clock Tree and Power Rules

- The clock tree is the most mis-configured part: validate every derived frequency (AHB/APB1/APB2/timer clocks — APB timers run at 2× when prescaler ≠1; USB needs exact 48 MHz; ADC max clock per datasheet).
- Use HSE (crystal) for anything needing UART accuracy at high baud or USB; HSI drifts with temperature — quantify baud error if you rely on it.
- `HAL_Delay()` depends on SysTick; if SysTick priority is misconfigured under RTOS, delays hang. Under FreeRTOS use `vTaskDelay`, and raise SysTick priority per the FreeRTOS STM32 port requirements.
- Low power: run/stop/standby/shutdown modes with very different wake sources and retention — state which peripherals stay clocked; RTC + LSE required for standby timekeeping; verify wake time budget (HSI startup, PLL relock) against application latency.
- Enable brown-out (BOR) and independent watchdog (IWDG, LSI-clocked — can't be stopped by software) for production.

## 4. Peripheral Traps (the flaws that bite)

- **I2C**: HAL blocking I2C in an ISR context deadlocks; I2C peripheral locks up on bus glitches — implement bus recovery (toggle SCL via GPIO bit-bang, re-init peripheral). Check errata for I2C on F1 (known issues).
- **UART**: overrun errors halt reception until ORE cleared — in the HAL, enable error callbacks and clear flags; use IDLE-line interrupt + DMA for variable-length protocols (the standard robust pattern).
- **ADC**: calibrate (`HAL_ADCEx_Calibration_Start`) after every clock change; sampling time vs. source impedance — long sampling time for high-impedance sources or readings bleed across channels; injected vs. regular conversions for motor control timing.
- **Timers**: update interrupt doesn't fire on first config without forcing an update event (UG bit) — classic "timer starts late" bug; PWM center-aligned mode changes frequency math (÷2).
- **USB**: needs 48 MHz ±0.25%; VBUS sensing pin config varies by board — wrong config = device never enumerates on some hosts.
- **F1 clones (HK32/GD32/CH32)**: register-compatible mostly, but flash wait states, ADC behavior, and USB differ — verify every peripheral against the clone's datasheet, never assume ST equivalence.

## 5. DMA and Interrupt Architecture

- Standard robust UART RX: circular DMA + IDLE interrupt, process in task — no per-byte interrupts.
- DMA on H7: D-cache coherency — either place DMA buffers in non-cacheable MPU regions (D2/D3 SRAM) or clean/invalidate cache around transfers. Forgetting this causes intermittent data corruption that appears "random."
- DMA priority vs. peripheral data rate: set very-high priority for ADC/audio streams; underruns/overruns are silent without error interrupts — enable them.
- NVIC: set priority grouping explicitly (`NVIC_PRIORITYGROUP_4` under FreeRTOS); every interrupt used with RTOS API calls must be at/below `configMAX_SYSCALL_INTERRUPT_PRIORITY` (numerically ≥ its value).

## 6. Flash, Bootloader, and Protection

- Flash write/erase stalls CPU on single-bank parts — never erase while real-time tasks run; execute flash routines from RAM where required.
- Option bytes: configure RDP level (readout protection L1 for production — L2 is irreversible), BOR level, IWDG hardware enable. Document the production option-byte programming step; verify with a test unit (RDP L1 blocks debugging — plan firmware signing-off before enabling).
- Custom bootloader layout: vector table relocation (`SCB->VTOR`) in the app; bootloader validates CRC before jump; app marks itself valid after self-test (see microcontrollers.md §6).
- Dual-bank parts (L4+, G4, H7 some) enable safe swap OTA — prefer them for field-updatable products.

## 7. Debugging with SWD

- ST-Link + SWD: keep SWD pins free in the pin map (don't reassign PA13/PA14); under low-power modes debug attach fails — document how to recover (connect-under-reset).
- `SWV`/ITM trace for printf-style debug without UART; ETM trace on larger parts via J-Trace for timing analysis.
- Semihosting is debug-only — strip from release builds (it hangs without a debugger attached on some configs).
- Fault diagnosis: on HardFault read SCB->CFSR/HFSR/BFAR/MMAR — implement a fault handler that logs these (see reliability-testing.md §1); CubeIDE's Fault Analyzer visualizes them.
