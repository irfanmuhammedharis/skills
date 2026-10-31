# Using the Hangshun SDK under PlatformIO with arm-none-eabi-gcc

Read `clocks-and-hk-extensions.md` first. Most people who think they need this
do not: 96 and 120 MHz are reachable with plain ST CMSIS headers. Come here
only for the cache controller, flash encryption, the UID driver, HSI 28/56 MHz,
or the `RCC->CFGR4`/`CFGR5` extended clock domains.

## What the SDK is, and what it is missing

The package is `HK32F103x8xBT6A_SDK`, covering the **A**-series parts. Layout:

```
SDK/Libraries/CMSIS/HK32F103xxxxA/
    Include/  hk32f103xxxxa.h  hk32f103xxxxa_conf.h  hk32f103xxxxa_def.h
              system_hk32f103xxxxa.h
    Source/   system_hk32f103xxxxa.c
              ARM/startup_hk32f103xxxxa.s     <- Keil ARMASM syntax
              IAR/IAR_Startup_hk32f103xxxxa.s <- IAR syntax
SDK/Libraries/HK32F103xxxxA_StdPeriphDriver/  <- 24 drivers, StdPeriph style
SDK/Libraries/HK32F103xxxxA-USB-FS-Device-Driver/
```

Drivers: adc, bkp, **cache**, can, crc, dac, dbgmcu, dma, exti, flash, fsmc,
gpio, i2c, iwdg, misc, pwr, rcc, rtc, sdio, spi, tim, **uid**, usart, wwdg.

**There is no GCC startup file and no GCC linker script anywhere in the SDK.**
That is the whole cost of this path. Everything else is ordinary
StdPeriph-style C that GCC compiles without complaint.

Get the SDK from Hangshun (hkmicrochip.com) or their Gitee. Third-party GitHub
mirrors exist — e.g. `amir1387aht/HK32F103CBT6A` — and are convenient, but the
vendor is the authority for the datasheet and user manual.

## The shortcut that makes this cheap

The HK32F103xxxxA interrupt vector table is **identical to the STM32F103
high-density table**: IRQ 0 `WWDG_IRQn` through IRQ 59 `DMA2_Channel4_5_IRQn`,
same numbers, same names, including `FSMC_IRQn = 48` and `SDIO_IRQn = 49`.

So you do not have to translate the Keil `.s` file. Reuse ST's GCC startup:

```
~/.platformio/packages/framework-cmsis-stm32f1/Source/Templates/gcc/startup_stm32f103xe.s
```

It has the right vector table, the right weak default handlers, and correct
GNU-as syntax. It calls `SystemInit` before `main`, which is exactly where the
vendor's `system_hk32f103xxxxa.c` wants to be.

Do **not** use `startup_stm32f103xb.S` — the medium-density table stops at
IRQ 42 and you lose TIM5–8, SPI3, UART4/5, FSMC, SDIO, ADC3 and DMA2.

## Project layout

```
project/
├── platformio.ini
├── hk32f103.ld                 # linker script (see below)
├── startup_hk32f103.s          # copy of ST's startup_stm32f103xe.s
├── src/
│   └── main.c
└── hk32sdk/                    # vendor SDK, trimmed
    ├── CMSIS/HK32F103xxxxA/Include/*.h
    ├── CMSIS/HK32F103xxxxA/Source/system_hk32f103xxxxa.c
    └── StdPeriphDriver/{inc,src}
```

```ini
[env:hk32_sdk]
platform = ststm32
board = genericSTM32F103C8
; no framework -- we supply CMSIS core, startup and drivers ourselves
board_build.ldscript = $PROJECT_DIR/hk32f103.ld
build_src_filter =
  +<*>
  +<../startup_hk32f103.s>
  +<../hk32sdk/CMSIS/HK32F103xxxxA/Source/system_hk32f103xxxxa.c>
  +<../hk32sdk/StdPeriphDriver/src/*.c>
build_flags =
  -DHSE_VALUE=8000000U
  -DUSE_STDPERIPH_DRIVER
  -I hk32sdk/CMSIS/HK32F103xxxxA/Include
  -I hk32sdk/StdPeriphDriver/inc
  -mcpu=cortex-m3 -mthumb
  -Os -ffunction-sections -fdata-sections
build_unflags = -DSTM32F103xB -DSTM32F1
```

Omitting `framework` means PlatformIO does not pull in ST's CMSIS device
headers, so `stm32f1xx.h` and `hk32f103xxxxa.h` cannot collide. You do still
need the ARM CMSIS **core** headers (`core_cm3.h`); the vendor SDK ships its
own copy under `CMSIS/CM3/Core` — add that to the include path too.

## Linker script

Start from ST's and edit the memory regions:

```
~/.platformio/packages/tool-ldscripts-ststm32/stm32f1/STM32F103C8TX_FLASH.ld
```

```
MEMORY
{
  RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 20K
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 64K   /* 128K on CB parts */
}
```

Everything else in ST's script — section placement, `_estack`, `.isr_vector`,
`_sidata`/`_sdata`/`_edata`/`_sbss`/`_ebss` — matches what ST's startup code
expects, so leave it alone.

Verify the script was actually used: `pio run -v | grep '\.ld'`. An
unreadable or empty script can still produce a "SUCCESS" build with a
meaningless layout.

## Configuring the vendor system file

`system_hk32f103xxxxa.c` selects the clock at compile time by which macro is
uncommented near the top:

```c
#define SYSCLK_SOURCE   SYSCLK_SRC_PLL
#define SYSCLK_HSE8M_PLL_FREQ_72MHz   72000000
//#define SYSCLK_HSE8M_PLL_FREQ_96MHz   96000000
//#define SYSCLK_HSE8M_PLL_FREQ_120MHz  120000000
```

Edit the file rather than trying to drive it from `build_flags` — the
`#if defined` chain checks for definition, and PlatformIO's `-D` would be
overridden by the file's own `#define` anyway.

## Order of work

1. Get a blink building with `framework = cmsis` and no SDK at all. Confirm
   the board, the wiring, and the upload path work.
2. Only then swap in the SDK. If the SDK build misbehaves you want to already
   know the hardware is fine.
3. Add drivers one at a time to `build_src_filter`; the StdPeriph sources have
   few interdependencies beyond `misc.c` and `rcc.c`.

## Failure modes

| Symptom | Cause |
|---|---|
| Hundreds of redefinition errors | ST CMSIS headers still in the include path — remove `framework`, and `build_unflags` the `STM32F103xB`/`STM32F1` defines |
| `undefined reference to SystemInit` | `system_hk32f103xxxxa.c` not in `build_src_filter` |
| `Error: bad instruction` in the startup file | you kept the vendor's Keil `.s`; use ST's GCC one |
| Hard fault immediately at reset | linker script memory regions wrong, or `_estack` not at the top of RAM |
| Runs, but every interrupt above IRQ 42 goes to the default handler | medium-density startup — switch to `startup_stm32f103xe.s` |
| `core_cm3.h: No such file` | vendor CMSIS CM3 core directory missing from `-I` |
