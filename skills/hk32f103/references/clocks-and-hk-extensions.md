# Clocks above 72 MHz, and the rest of the HK-only silicon

Facts here are read out of Hangshun's own `HK32F103xxxxA` SDK
(`system_hk32f103xxxxa.c`, `hk32f103xxxxa.h`, `hk32f103xxxxa_flash.h`). They
describe the **A**-series parts. On a non-A `HK32F103C8T6`, treat the vendor
rating (96 MHz) as the ceiling and verify anything else on the device.

## The good news: 96 and 120 MHz do not need the vendor SDK

This is the single most useful thing to know, and it is easy to get wrong.

The vendor's own 96 MHz and 120 MHz routines use the **standard** `RCC->CFGR`
PLL multiplier field:

- 96 MHz = HSE 8 MHz × **12**, flash latency **4**
- 120 MHz = HSE 8 MHz × **15**, flash latency **6**

Both multipliers exist in ST's CMSIS headers (`RCC_CFGR_PLLMULL12`,
`RCC_CFGR_PLLMULL15`; in HAL, `RCC_PLL_MUL12` / `RCC_PLL_MUL15` in
`stm32f1xx_hal_rcc_ex.h`). And `FLASH_ACR_LATENCY` is a **3-bit** field
(`FLASH_ACR_LATENCY_Msk == 0x7`) in ST's headers too — ST only *defines*
values 0–2 because 72 MHz is its ceiling, but 4 and 6 are writable.

So you can clock an HK32F103 well past 72 MHz from a plain
`framework = cmsis` or `framework = stm32cube` project. You only have to stop
using `HAL_RCC_ClockConfig()` for the flash-latency step, since
`IS_FLASH_LATENCY()` accepts nothing above `FLASH_LATENCY_2`.

### Verified-to-compile 96 MHz setup (CMSIS, no vendor SDK)

```c
#include "stm32f1xx.h"

static void clock_96mhz(void) {
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY)) { }

    /* Flash latency 4. ST defines only 0..2, but ACR.LATENCY is 3 bits. */
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | 4U;

    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    RCC->CFGR |= RCC_CFGR_HPRE_DIV1      /* HCLK  = SYSCLK = 96 MHz */
              |  RCC_CFGR_PPRE1_DIV2     /* PCLK1 = 48 MHz          */
              |  RCC_CFGR_PPRE2_DIV1;    /* PCLK2 = 96 MHz          */

    RCC->CFGR &= ~(RCC_CFGR_PLLSRC | RCC_CFGR_PLLXTPRE | RCC_CFGR_PLLMULL);
    RCC->CFGR |= RCC_CFGR_PLLSRC         /* set == HSE as PLL source */
              |  RCC_CFGR_PLLMULL12;

    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY)) { }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) { }

    SystemCoreClock = 96000000U;
}
```

Note `RCC_CFGR_PLLSRC` in ST's headers is the bit itself (set = HSE); there is
no `RCC_CFGR_PLLSRC_HSE`.

For 120 MHz: `RCC_CFGR_PLLMULL15` and latency `6U`. Everything else is
identical. Raising `SystemCoreClock` matters — `SysTick_Config()`, HAL's tick
and every baud-rate calculation derive from it.

### Vendor clock recipes, for reference

From `system_hk32f103xxxxa.c`, HSE = 8 MHz, standard `RCC->CFGR` PLL:

| SYSCLK | Multiplier | Flash latency (ACR) |
|---|---|---|
| 24 MHz | ×3 | 0 |
| 48 MHz | ×6 | 1 |
| 72 MHz | ×9 | 2 |
| 90.285 MHz | prediv 7, extended mul 79 | 3 |
| 96 MHz | ×12 | 4 |
| 98 MHz | prediv 4, extended mul 49 | 4 |
| 120 MHz | ×15 | 6 |

The HSI-PLL variants (64 / 72 / 89.6 / 96 / 98 / 120 MHz) exist too, and are
useful if the board has no crystal.

**Caveat that matters at 96 and 120 MHz:** APB1 on this die is still an
STM32F103-style bus. The vendor code sets `PPRE1_DIV2` at both 96 and
120 MHz, giving PCLK1 = 48 and 60 MHz — above the STM32F103's 36 MHz APB1
limit. Hangshun evidently rates it higher, but if an APB1 peripheral (USART2/3,
I2C, TIM2–7, CAN, USB) misbehaves at high SYSCLK, drop to `PPRE1_DIV4` before
suspecting anything else. USB in particular needs exactly 48 MHz from the
USB prescaler, which the ×12/×15 PLL settings cannot produce — **USB FS and
96/120 MHz are mutually exclusive on this part.** Stay at 72 MHz if you need
USB.

## What genuinely requires the vendor SDK

These have no counterpart anywhere in ST's headers.

### Extended RCC registers

`RCC_TypeDef` on the HK32 continues past ST's:

```c
__IO uint32_t CFGR2;      /* ST has this on connectivity-line parts */
__IO uint32_t CFGR3;
__IO uint32_t CR2;
/* ... reserved ... */
__IO uint32_t HSECTL;     /* HSE control     */
__IO uint32_t PLLCTL;     /* extended PLL    */
__IO uint32_t CFGR4;      /* extended PLLMUL + PLL source select */
__IO uint32_t CFGR5;      /* extended clock switch               */
__IO uint32_t AHBRST2;
__IO uint32_t AHBRST3;
__IO uint32_t LSICTL;
```

`RCC->CFGR4` carries a second PLL multiplier field with values ×16, ×32, ×48,
×64, ×80, ×96, ×112 (`RCC_CFGR4_PLLMULLnn`, 3 bits), plus a PLL-source select
`PPSS` that can take **HSI 56 MHz** as the PLL input. `RCC->CFGR5` switches an
extended clock domain between LSE / LSI / HSI56M / HSI28M / an external clock
input selectable on PA1, PB1 or PC7.

### HSI at 8, 28 or 56 MHz

`HSI8M_VALUE`, `HSI28M_VALUE`, `HSI56M_VALUE`. ST's HSI is fixed at 8 MHz, so
running crystal-free above 8 MHz — or PLLing from a 56 MHz internal source —
is HK-only territory.

### Flash latency beyond 7

`FLASH->LATENCY_EX` at offset 0x80 adds two more latency bits on top of the
3-bit `ACR.LATENCY`. The SDK's `FLASH_Latency_*` constants run to
`FLASH_Latency_31`. You will not need this below 120 MHz.

### Flash controller extras

`FLASH_TypeDef` gains, past ST's layout:

```c
__IO uint32_t LATENCY_EX;   /* 0x80 */
__IO uint32_t ECR;
__IO uint32_t ENCRY_CFG;    /* flash encryption */
__IO uint32_t DECRY_CFG;
__IO uint32_t UKEYL, UKEYH; /* user key */
__IO uint32_t PW0, PW1, PW2, PW3;
```

`ACR`, `KEYR`, `OPTKEYR`, `SR`, `CR`, `AR`, `OBR`, `WRPR` are at the ST
offsets with ST semantics, which is why OpenOCD's `stm32f1x` flash driver
works.

### Peripherals with no ST equivalent

- **Cache controller** — `hk32f103xxxxa_cache.c`. No F1 equivalent.
- **UID driver** — `hk32f103xxxxa_uid.c`. Do not read `0x1FFFF7E0` and assume
  it is ST's unique ID block.
- **SAI-adjacent clocking** — the 90.285 / 98 MHz recipes exist specifically
  to land on usable audio clocks (`SAI_EXT_CLK` = 49152000).

## Practical rule

Write the clock setup by hand against `stm32f1xx.h` for anything up to
120 MHz. Pull in the vendor SDK only for the cache, flash encryption, UID, the
HSI 28/56 MHz sources, or the `CFGR4`/`CFGR5` extended domains — and read
`vendor-sdk-gcc.md` first, because that path costs you a startup file and a
linker script.
