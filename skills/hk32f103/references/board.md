# The HK32F103C8T6 development board

## Which board is it

"HK32F103C8T6 development board" almost always means a blue-pill-form clone:
a 2×20 DIP-form PCB with the LQFP48 part, micro-USB or USB-C at one end, a
4-pin SWD header at the other, two jumper pairs for BOOT0/BOOT1, an 8 MHz HSE
crystal and a 32.768 kHz LSE crystal. Hangshun's own eval boards
(HK32F103VE, LQFP100) are a different thing entirely — more pins, on-board
peripherals, and a vendor schematic in the SDK under `Documents/5_Hardware`.

Confirm before relying on any pinout below:

- Chip marking — `HK32F103C8T6` vs `...C8T6A` vs `...CBT6A`. See SKILL.md
  Step 0; the `A` suffix changes the clock ceiling.
- Count the pins: 48 = C-series (this page), 100 = V-series.
- Look for the LED. Blue-pill clones put it on **PC13**, active low. Some
  clones move it. Toggle PC13 and see.

## Pinout (LQFP48, pin-compatible with STM32F103C8T6)

The vendor's whole selling point is pin compatibility, so any STM32F103C8T6
blue-pill pinout diagram applies. The parts you actually reach for:

| Function | Pins |
|---|---|
| LED (blue-pill clones) | PC13, active low, 2 MHz / 3 mA max — LED only |
| SWD | PA13 = SWDIO, PA14 = SWCLK |
| USART1 | PA9 = TX, PA10 = RX |
| USART2 | PA2 = TX, PA3 = RX |
| USART3 | PB10 = TX, PB11 = RX |
| USB FS | PA11 = D−, PA12 = D+ |
| SPI1 | PA5 SCK, PA6 MISO, PA7 MOSI, PA4 NSS |
| SPI2 | PB13 SCK, PB14 MISO, PB15 MOSI, PB12 NSS |
| I2C1 | PB6 SCL, PB7 SDA (or PB8/PB9 remapped) |
| I2C2 | PB10 SCL, PB11 SDA |
| ADC1 | PA0–PA7, PB0, PB1 |
| HSE crystal | PD0/PD1 (OSC_IN / OSC_OUT), 8 MHz |
| LSE crystal | PC14/PC15, 32.768 kHz |
| Boot | BOOT0 jumper, BOOT1 = PB2 |

PA13/PA14 are SWD at reset. Reassigning them in firmware locks you out of the
debugger on the next boot — recover via BOOT0 (see `flashing-and-debug.md`).

PC13, PC14 and PC15 sit in the backup domain: limited drive, and unusable as
normal GPIO if you are using the LSE or the RTC.

## Boot jumpers

| BOOT1 | BOOT0 | Boots from |
|---|---|---|
| x | 0 | user flash — normal running |
| 0 | 1 | system memory — UART bootloader |
| 1 | 1 | embedded SRAM |

Leave BOOT0 at 0 for normal use. The most common "I flashed it and nothing
happened" is a BOOT0 jumper left at 1.

## Power

- 5 V pin → on-board regulator → 3.3 V. USB feeds the same rail.
- 3V3 pin bypasses the regulator; feed it 3.3 V only.
- **Do not power from USB and from an ST-Link's 3.3 V pin at the same time.**
- The MCU is 3.3 V. Several pins are 5 V tolerant, but do not assume it — the
  analog pins are not.

## USB, and the two things that break it

1. Many clone boards ship the wrong D+ pull-up resistor (1.5 kΩ from PA12 to
   3.3 V is required; boards commonly fit 4.7 kΩ or 10 kΩ). Symptom:
   intermittent or absent enumeration. Fix is a 1.5 kΩ from PA12 to 3.3 V,
   often soldered across the existing part.
2. USB FS needs exactly 48 MHz from the USB prescaler, which the PLL settings
   for 96 and 120 MHz cannot produce. **USB and >72 MHz are mutually
   exclusive on this part.** Stay at 72 MHz if you need USB.

Boards also arrive with no USB bootloader in flash — `upload_protocol = dfu`
will not work until you flash one over SWD first.

## Sanity check before debugging anything else

Flash the CMSIS blink from `platformio-ini.md` over SWD. If PC13 blinks, the
board, the crystal, the regulator, the programmer and the toolchain are all
good, and any later problem is in your code. If it does not, work through the
triage table in `flashing-and-debug.md` before changing project settings.
