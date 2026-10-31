# platformio.ini for HK32F103

All configurations below were built locally against `platform = ststm32`
19.6.0 with `toolchain-gccarmnoneeabi` 7.2.1. There is no `hk32` platform and
no HK board manifest — `genericSTM32F103C8` is the board you use.

## Framework choice

| Framework | Works | Use it when |
|---|---|---|
| `cmsis` | yes, verified | bare-metal register work; smallest footprint (300 B blink) |
| `stm32cube` | yes, verified | you want ST's HAL/LL drivers |
| `arduino` | yes, verified | STM32duino API; ~12 KB blink |
| `libopencm3` | supported by the board manifest | you prefer libopencm3's API |

None of them know anything about HK32 extensions. They all target the
STM32F103-compatible subset.

## Bare-metal (CMSIS)

```ini
[env:hk32f103c8]
platform = ststm32
board = genericSTM32F103C8
framework = cmsis
upload_protocol = stlink
debug_tool = stlink
build_flags = -DHSE_VALUE=8000000U
```

```c
#include "stm32f1xx.h"

static void delay(volatile uint32_t n) { while (n--) __NOP(); }

int main(void) {
    RCC->APB2ENR |= RCC_APB2ENR_IOPCEN;
    GPIOC->CRH &= ~(GPIO_CRH_CNF13 | GPIO_CRH_MODE13);
    GPIOC->CRH |= GPIO_CRH_MODE13_1;          /* output 2 MHz, push-pull */
    for (;;) {
        GPIOC->ODR ^= GPIO_ODR_ODR13;
        delay(500000);
    }
}
```

PC13 sinks the LED on blue-pill-form boards, so the LED is on when the pin is
low. PC13 is also limited to 2 MHz and 3 mA — do not drive anything but an LED
from it.

## STM32Cube HAL, clocked to 72 MHz

```ini
[env:hk32_hal]
platform = ststm32
board = genericSTM32F103C8
framework = stm32cube
build_flags = -DHSE_VALUE=8000000U
```

```c
#include "stm32f1xx_hal.h"

void SysTick_Handler(void) { HAL_IncTick(); }

static void clock_72mhz(void) {
    RCC_OscInitTypeDef osc = {0};
    RCC_ClkInitTypeDef clk = {0};
    osc.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    osc.HSEState       = RCC_HSE_ON;
    osc.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
    osc.PLL.PLLState   = RCC_PLL_ON;
    osc.PLL.PLLSource  = RCC_PLLSOURCE_HSE;
    osc.PLL.PLLMUL     = RCC_PLL_MUL9;        /* 8 MHz x 9 = 72 MHz */
    HAL_RCC_OscConfig(&osc);

    clk.ClockType      = RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK |
                         RCC_CLOCKTYPE_PCLK1  | RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
    clk.AHBCLKDivider  = RCC_SYSCLK_DIV1;
    clk.APB1CLKDivider = RCC_HCLK_DIV2;       /* APB1 max 36 MHz */
    clk.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_2);
}
```

72 MHz is the ceiling reachable this way. `RCC_PLL_MUL9` is the largest
multiplier ST's `RCC_CFGR` exposes and `FLASH_LATENCY_2` the largest wait-state
value; going higher needs HK-only registers
(→ `clocks-and-hk-extensions.md`).

## Arduino / STM32duino

```ini
[env:hk32_arduino]
platform = ststm32
board = genericSTM32F103C8
framework = arduino
upload_protocol = stlink
board_build.f_cpu = 72000000L
monitor_speed = 115200
```

```cpp
#include <Arduino.h>
void setup() { pinMode(PC13, OUTPUT); Serial.begin(115200); }
void loop()  { digitalWrite(PC13, !digitalRead(PC13)); delay(500); }
```

First build downloads the STM32duino core and takes a couple of minutes.

`Serial` maps to USART1 (PA9 TX / PA10 RX) by default. For USB CDC add
`build_flags = -DUSBCON -DUSBD_USE_CDC` — but only if the board actually has
the USB connector and the 1.5 kΩ D+ pull-up; see `board.md`.

## Flash and RAM size

`genericSTM32F103C8` declares 64 KB flash / 20 KB RAM. Two situations need
changing that.

**You have a CB part (128 KB), or a C8 part that really has 128 KB.** Many
F103C8-class dies — clones included — have the full 128 KB with only 64 KB
declared. Verify it on your own chip before relying on it: erase, write a
pattern past 0x08010000, read it back, power-cycle, read again.

```ini
[env:hk32f103cb_128k]
platform = ststm32
board = genericSTM32F103C8
framework = cmsis
board_build.mcu = stm32f103cbt6      ; selects the 128 KB linker script
board_upload.maximum_size = 131072   ; makes the size check agree
build_flags = -DHSE_VALUE=8000000U
```

Verified: this makes PlatformIO link with
`tool-ldscripts-ststm32/stm32f1/STM32F103CBUX_FLASH.ld` and report
`131072 bytes`. `board_upload.maximum_size` alone only changes the size
*report* — without `board_build.mcu` the linker still enforces 64 KB.

**Trap:** if you point `board_build.ldscript` at a path that does not exist or
is empty, the build can still report SUCCESS while producing a firmware with a
nonsense layout (an empty script gave "0 bytes used"). After any linker-script
override, check the size report is plausible and confirm the script that was
actually used with `pio run -v | grep '\.ld'`.

A custom script, if you need one:

```ini
board_build.ldscript = $PROJECT_DIR/hk32f103.ld
```

Start from `~/.platformio/packages/tool-ldscripts-ststm32/stm32f1/STM32F103C8TX_FLASH.ld`
and edit the `FLASH` region `LENGTH`.

## Multi-environment layout

```ini
[env]
platform = ststm32
board = genericSTM32F103C8
build_flags = -DHSE_VALUE=8000000U
monitor_speed = 115200

[env:debug]
framework = cmsis
build_type = debug
debug_tool = stlink
build_flags = ${env.build_flags} -DDEBUG -Og -g3

[env:release]
framework = cmsis
build_flags = ${env.build_flags} -DNDEBUG -Os
```

## Things that do not work

- `board = hk32f103c8` — no such board. `pio boards hk32` returns nothing.
- `platform = hk32` — does not exist.
- `board_debug.openocd_extra_args` — parsed, but not applied to the upload
  command on ststm32 19.6.0 (see `flashing-and-debug.md`).
- STM32CubeMX-generated projects assume ST silicon; the generated code is fine
  for the compatible subset but its clock configuration will not go past
  72 MHz on this part.
