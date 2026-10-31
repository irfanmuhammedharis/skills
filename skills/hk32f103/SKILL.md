---
name: hk32f103
description: "Build, flash and debug HK32F103 (Hangshun / 航顺) Cortex-M3 boards — HK32F103C8T6, C8T6A, CBT6A, VET6 — in PlatformIO. Use when a project targets an HK32F103 'blue pill' clone, when deciding whether to treat it as an STM32F103 or use the vendor SDK, when a build must run above 72 MHz, when ST-Link/OpenOCD refuses to identify the chip, when STM32CubeProgrammer rejects it, or when porting the Keil/IAR-only HK32 SDK to arm-none-eabi-gcc."
---

# HK32F103 in PlatformIO

The HK32F103 is Shenzhen Hangshun's Cortex-M3 part sold as a drop-in for the
STM32F103. Everything about working with it in PlatformIO follows from one
fact:

**PlatformIO has no `hk32` platform and no HK32 board definition. You build it
as an STM32F103 — and that works, right up to the point where you touch
something ST's headers do not know exists.**

The HK32F103 is a *superset*, not a copy. The STM32F103 register map is there
and correct; the vendor then bolted on extra RCC registers, extra flash-latency
bits, a cache controller and flash encryption. ST's CMSIS/HAL headers describe
none of it. So the whole job is knowing which side of that line you are on.

## Step 0 — establish which part you actually have

Never assume from the silkscreen on the board; read the chip.

| Marking | What it is | Max SYSCLK | Notes |
|---|---|---|---|
| `STM32F103C8T6` | genuine ST | 72 MHz | not this skill |
| `HK32F103C8T6` | Hangshun | vendor-rated **96 MHz** | 64 KB flash, 20 KB RAM |
| `HK32F103C8T6A` / `CBT6A` | Hangshun "A" series | **120 MHz** | the SDK family is `HK32F103xxxxA` |
| `HK32F103VET6` | Hangshun, LQFP100 | 120 MHz | vendor eval board part |

The `A` suffix matters: the public vendor SDK is `HK32F103x8xBT6A`, i.e. it
documents the **A** parts. A non-A `HK32F103C8T6` is closer to a plain
STM32F103 and the A-series extras may not be present. If the user has a non-A
part, do not promise 120 MHz or the cache/encryption features.

Confirming over SWD, if a debugger is attached: all the F103 clones report
Cortex-M3 **r2p1** where genuine ST parts report r1p1, and HK parts show ROM
table designer `0x55` / part `0x29b`. That is enough to tell HK from ST, GD,
CS and APM parts.

Also confirm the board itself — most HK32F103C8T6 boards are blue-pill-form
clones (LED on PC13, 8 MHz HSE crystal, BOOT0/BOOT1 jumpers, SWD header), but
vendor eval boards are not. See `references/board.md`.

## Step 1 — the default configuration, which is almost always right

```ini
[env:hk32f103c8]
platform = ststm32
board = genericSTM32F103C8
framework = cmsis          ; or stm32cube, arduino, libopencm3
upload_protocol = stlink
debug_tool = stlink
build_flags = -DHSE_VALUE=8000000U
```

This is verified to build clean on `ststm32` 19.6.0 with `cmsis`,
`stm32cube` and `arduino`. Use it for anything at or below 72 MHz that only
touches STM32F103 peripherals — GPIO, USART, SPI, I2C, TIM, ADC, DMA, RTC,
IWDG/WWDG, CAN, USB FS. Those are at the STM32F103 addresses with the
STM32F103 bit layouts, so ST's headers, ST's HAL and STM32duino all work
unmodified.

Full recipes per framework, flash/RAM size overrides for the CB (128 KB)
parts, and the linker-script trap → `references/platformio-ini.md`.

## Step 2 — decide whether you are past the compatibility line

Two questions, in this order.

### "I need more than 72 MHz" — you probably do *not* need the vendor SDK

This is the most common wrong turn. Hangshun's own 96 and 120 MHz routines use
the **standard** `RCC->CFGR` PLL multiplier — 96 MHz is HSE 8 MHz × 12,
120 MHz is × 15 — and both multipliers already exist in ST's headers
(`RCC_CFGR_PLLMULL12`, `RCC_CFGR_PLLMULL15`). `FLASH_ACR_LATENCY` is a 3-bit
field in ST's headers too, so the latency values those speeds need (4 and 6)
are writable; ST simply never defines constants above `FLASH_LATENCY_2`
because 72 MHz is its own ceiling.

So a plain `framework = cmsis` project clocks this part to 96 or 120 MHz. You
just write the RCC sequence by hand instead of calling
`HAL_RCC_ClockConfig()`, whose `IS_FLASH_LATENCY()` will not accept the
latency. A verified-to-compile 96 MHz function is in
`references/clocks-and-hk-extensions.md`.

Two constraints come with it: USB FS cannot work above 72 MHz on this part
(the ×12/×15 PLL cannot feed the USB prescaler its required 48 MHz), and APB1
ends up above the STM32F103's 36 MHz limit at those speeds.

### "I need HK-only silicon" — now you need the vendor SDK

| HK32-only feature | Register / driver | Why ST headers cannot reach it |
|---|---|---|
| HSI at 28 MHz or 56 MHz | `HSI28M_VALUE`, `HSI56M_VALUE` | ST's HSI is fixed at 8 MHz |
| Extended PLL (×16…×112), PLL from HSI56M | `RCC->CFGR4`, `RCC->PLLCTL`, `RCC->HSECTL` | registers absent from `stm32f1xx.h` |
| Extended clock-domain switch (LSE/LSI/HSI56/HSI28/ext pin) | `RCC->CFGR5` | absent |
| Flash wait states above 7 | `FLASH->LATENCY_EX` (offset 0x80) | absent |
| Flash cache controller | `hk32f103xxxxa_cache.c` | no F1 equivalent |
| Flash encryption | `FLASH->ENCRY_CFG`, `DECRY_CFG`, `UKEYL/UKEYH`, `PW0..PW3` | no F1 equivalent |
| Unique-ID | `hk32f103xxxxa_uid.c` | not at ST's `0x1FFFF7E0` |
| `RCC->AHBRST2/3`, `RCC->LSICTL` | extended reset/clock control | absent |

Crossing this line has a real cost, worth saying out loud before starting:
**the vendor SDK ships startup files for Keil (ARMASM) and IAR only — there is
no GCC startup and no GCC linker script.** Using it under PlatformIO means
supplying both. It is less work than it sounds, because the HK32F103xxxxA
interrupt vector table is byte-for-byte the STM32F103 **high-density** table
(IRQ 0–59), so ST's `startup_stm32f103xe.s` drops straight in. Full recipe:
`references/vendor-sdk-gcc.md`.

## Step 3 — flashing

ST-Link over SWD with OpenOCD's `stm32f1x` driver is the normal path and
usually just works; the chip presents an STM32F103-compatible flash
controller at the same addresses with the same 1 KB/2 KB page structure.

Two things to know up front:

- **STM32CubeProgrammer refuses these parts.** ST does not support non-ST
  silicon. Use OpenOCD, Keil's ST-Link utility, `stlink` (`st-flash`), or the
  serial bootloader. Do not send a user to CubeProgrammer.
- OpenOCD's `stm32f1x.cfg` checks the SWD TAP id against `0x1ba01477` and
  auto-probes flash size from the ST flash-size register. Either can trip on a
  clone. Both are overridable.

Wiring, the exact override commands, BOOT0 handling, RDP unlock, serial
bootloader and the failure-to-fix triage table →
`references/flashing-and-debug.md`.

One PlatformIO-specific gotcha, verified on `ststm32` 19.6.0:
`board_debug.openocd_extra_args` in `platformio.ini` **does not reach the
upload command** — the board's debug tools are built before INI overrides are
applied. To pass extra OpenOCD `-c` commands during upload you need
`upload_protocol = custom` with an explicit `upload_command`. The reference
has the working line.

## Reference index

- `references/platformio-ini.md` — verified configs for cmsis / stm32cube /
  arduino / libopencm3, memory-size and linker-script overrides.
- `references/flashing-and-debug.md` — ST-Link, OpenOCD overrides, serial
  bootloader, DFU, debugging, error triage.
- `references/clocks-and-hk-extensions.md` — the HK-only registers, the clock
  tree above 72 MHz, flash latency table.
- `references/vendor-sdk-gcc.md` — porting the Keil/IAR vendor SDK to
  arm-none-eabi-gcc inside a PlatformIO project.
- `references/board.md` — blue-pill-form HK32F103C8T6 board: pinout, jumpers,
  power, USB, and how to verify what you have.

## Honest limits

The register-level facts above come from Hangshun's own `HK32F103xxxxA` SDK
headers, and the build recipes were compiled locally. The parts that depend on
your specific silicon and programmer — the reported IDCODE, whether the UART
system bootloader is present, whether a "64 KB" part actually has 128 KB —
have not been measured here. Where a reference tells you to check something on
the device, check it rather than trusting the table.
