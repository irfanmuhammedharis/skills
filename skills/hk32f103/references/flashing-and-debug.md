# Flashing and debugging an HK32F103

## What programs it, and what does not

| Tool | Works | Notes |
|---|---|---|
| ST-Link V2/V3 + OpenOCD `stm32f1x` | yes, normal path | PlatformIO's default `upload_protocol = stlink` |
| ST-Link + `stlink` (`st-flash`) | yes | independent of PlatformIO |
| J-Link | yes | `upload_protocol = jlink`, device `STM32F103C8` |
| CMSIS-DAP / DAPLink | yes | `upload_protocol = cmsis-dap` |
| Black Magic Probe | yes | `upload_protocol = blackmagic` |
| UART system bootloader (BOOT0=1) | usually — **verify on your part** | `upload_protocol = serial` |
| USB DFU | only with a DFU bootloader already flashed | not present from the factory |
| **STM32CubeProgrammer** | **no** | ST does not support non-ST silicon; it rejects the part |

Never route a user to STM32CubeProgrammer for this chip.

## SWD wiring

Blue-pill-form boards expose a 4-pin SWD header at the end opposite the USB
connector:

```
ST-Link V2          Board
--------------------------
SWDIO       <-->    SWDIO   (PA13)
SWCLK       <-->    SWCLK   (PA14)
GND         <-->    GND
3.3V        <-->    3V3     (only if the board is not otherwise powered)
```

Do not feed 3.3 V from the ST-Link while USB is also powering the board.

## Default upload

```ini
upload_protocol = stlink
debug_tool = stlink
```

PlatformIO then runs, in effect:

```
openocd -d1 -s <tool-openocd>/openocd/scripts \
        -f interface/stlink.cfg -c "transport select hla_swd" \
        -f target/stm32f1x.cfg \
        -c "program {firmware.elf} verify reset; shutdown;"
```

## `upload_protocol = stlink` fails: "Debug adapter doesn't support 'hla_swd'"

Hit this first on a real board, so it goes before the clone-specific stuff —
it is not a clone problem at all, and a genuine STM32F103 fails identically.

PlatformIO's ststm32 platform hardcodes `transport select hla_swd` whenever
`upload_protocol = stlink` (see `_add_default_debug_tools` in `platform.py`).
But `interface/stlink.cfg` in tool-openocd 3.1200.7 (OpenOCD 0.12) selects
`adapter driver st-link`, a dapdirect ARM-DAP wrapper that offers `swd` and
does **not** provide the deprecated `hla_swd` transport. The upload dies before
touching the target:

```
Debug adapter doesn't support 'hla_swd' transport
*** [upload] Error 1
```

Fix by driving OpenOCD yourself with `swd`:

```ini
upload_protocol = custom
upload_command = openocd -s ${platformio.packages_dir}/tool-openocd/openocd/scripts -f interface/stlink.cfg -c "transport select swd" -f target/stm32f1x.cfg -c "program {$BUILD_DIR/firmware.elf} verify reset; shutdown;"

debug_tool = custom
debug_server =
    ${platformio.packages_dir}/tool-openocd/bin/openocd
    -s
    ${platformio.packages_dir}/tool-openocd/openocd/scripts
    -f
    interface/stlink.cfg
    -c
    transport select swd
    -f
    target/stm32f1x.cfg
```

`$BUILD_DIR/firmware.elf` rather than `$SOURCE` — with a custom protocol
`$SOURCE` is `firmware.bin`, which would need an explicit `0x08000000`.

Verified working end to end on an HK32F103C8T6 with an ST-Link V2
(firmware V2J38S7): programmed, verified, reset.

## What a real HK32F103C8T6 reports

Measured, so you have something to compare against:

```
Info : SWD DPIDR 0x2ba01477
Info : [stm32f1x.cpu] Cortex-M3 r2p1 processor detected
Info : device id = 0x20036410
Info : flash size = 128 KiB
```

- **DPIDR `0x2ba01477`**, where a genuine STM32F103 reports `0x1ba01477`.
  This is why `stm32f1x.cfg`'s `-expected-id` check is worth knowing about —
  though note it did *not* fire here, because that check applies to the JTAG
  TAP id, not the SWD DPIDR.
- **Cortex-M3 r2p1**, the clone signature (ST ships r1p1).
- **device id `0x20036410`** — DEV_ID `0x410`, i.e. it presents as
  STM32F103 medium-density, which is exactly why OpenOCD's `stm32f1x` driver
  drives it without complaint. REV_ID `0x2003`.
- **flash size 128 KiB** on a part marked C8. The device's own flash-size
  register says so; this is not the usual "hidden 64 KB" folklore. See the
  128 KB config in `platformio-ini.md`.

## When the stock target config trips on the clone

`target/stm32f1x.cfg` does two things that can fail on non-ST silicon:

1. `swj_newdap ... -expected-id $_CPUTAPID`, defaulting to `0x1ba01477`
   (SWD) / `0x3ba00477` (JTAG). A different TAP id aborts the session.
2. `flash bank ... stm32f1x 0x08000000 $_FLASH_SIZE 0 0` with `_FLASH_SIZE`
   defaulting to `0`, i.e. auto-probe from ST's flash-size register. A wrong
   or absent value there gives a bank of the wrong size.

Both are overridable, and both overrides are plain OpenOCD variables:

```
-c "set CPUTAPID 0"            # 0 disables the id check entirely
-c "set FLASH_SIZE 0x10000"    # 64 KB; 0x20000 for 128 KB
```

They must be set **before** `-f target/stm32f1x.cfg` is sourced.

### Getting those into a PlatformIO upload

`board_debug.openocd_extra_args` does **not** work for uploads on ststm32
19.6.0 — verified. The platform builds each board's debug-tool server
arguments when the board manifest loads, which is before `board_*` INI
overrides are applied, so the extra args are silently dropped from the upload
command. Use a custom upload command instead:

```ini
[env:hk32]
platform = ststm32
board = genericSTM32F103C8
framework = cmsis
upload_protocol = custom
upload_command = openocd -s ${platformio.packages_dir}/tool-openocd/openocd/scripts -f interface/stlink.cfg -c "transport select hla_swd" -c "set FLASH_SIZE 0x10000" -c "set CPUTAPID 0" -f target/stm32f1x.cfg -c "program {$SOURCE} 0x08000000 verify reset; shutdown;"
```

Two details that bite:

- With `upload_protocol = custom`, `$SOURCE` is **`firmware.bin`**, not the
  ELF — so the load address `0x08000000` is mandatory. Omit it and OpenOCD
  writes to the wrong place or errors. Use `$BUILD_DIR/firmware.elf` instead
  if you would rather not think about addresses.
- Use `${platformio.packages_dir}` (INI interpolation).
  `$PLATFORMIO_CORE_DIR` expands to nothing here.

Verified: this produces a correct, launching OpenOCD invocation.

## Serial bootloader

```ini
upload_protocol = serial
upload_port = /dev/ttyUSB0
```

Sequence: BOOT0 jumper to 1, BOOT1 to 0, press reset, upload, move BOOT0 back
to 0, reset again. PlatformIO drives `tool-stm32flash`.

Wire a USB-TTL adapter to PA9 (board TX ← adapter RX) and PA10 (board RX ←
adapter TX), plus GND.

Whether Hangshun implements ST's UART bootloader protocol bit-for-bit is not
something to assume. If `stm32flash` cannot get an ACK after a correct BOOT0
sequence, fall back to SWD rather than chasing it.

## Debugging

```ini
debug_tool = stlink
debug_init_break = tbreak main
```

`pio debug` then works normally — GDB, breakpoints, stepping. The SVD ST
supplies (`STM32F103xx.svd`) gives you a peripheral register view that is
correct for the compatible subset and simply missing the HK-only registers
(`RCC->CFGR4`, `FLASH->LATENCY_EX`, …); those you inspect by address.

To pass OpenOCD overrides to the *debug* server (as opposed to upload), the
documented option does apply:

```ini
debug_server =
  ${platformio.packages_dir}/tool-openocd/bin/openocd
  -s
  ${platformio.packages_dir}/tool-openocd/openocd/scripts
  -f
  interface/stlink.cfg
  -c
  transport select hla_swd
  -c
  set FLASH_SIZE 0x10000
  -f
  target/stm32f1x.cfg
```

## Triage

| Symptom | Cause | Fix |
|---|---|---|
| `Error: init mode failed (unable to connect to the target)` | no SWD contact, or firmware disabled SWD pins | check wiring/GND; hold NRST low while connecting, or use `reset_config srst_only srst_nogate`, or boot from the bootloader (BOOT0=1) to get a clean chip |
| `expected 1 of 1: 0x1ba01477` TAP mismatch | clone reports a different TAP id | `-c "set CPUTAPID 0"` |
| `Cannot identify target as a STM32 family` | flash driver probe rejected the device id | `-c "set FLASH_SIZE 0x10000"` to skip auto-probe; if it persists the flash driver genuinely disagrees — use `st-flash` or the serial bootloader |
| Connects, but `flash write_image` fails / verify mismatch past some address | flash bank sized wrong by auto-probe | set `FLASH_SIZE` explicitly |
| `Target not halted` / device locked | read-out protection (RDP) set | `openocd -f ... -c "init; reset halt; stm32f1x unlock 0; reset run; shutdown"` — **this mass-erases the chip** |
| Works once, then never reconnects | application reconfigured PA13/PA14 away from SWD, or entered a low-power mode early | connect under reset, or BOOT0=1 |
| Upload succeeds, board does nothing | BOOT0 still jumpered to 1 | move BOOT0 back to 0 and reset |
| CubeProgrammer says "unknown device" | expected — ST tool, non-ST chip | use OpenOCD or `st-flash` |
| Blink runs at the wrong speed | `HSE_VALUE` mismatch, or PLL never engaged and you are on the 8 MHz HSI | set `-DHSE_VALUE=8000000U`, confirm the crystal, check `RCC->CFGR.SWS` reads PLL |

## Recovering a board that will not connect at all

1. BOOT0 jumper to 1, BOOT1 to 0.
2. Power-cycle. The core now runs the system bootloader from system memory, so
   whatever the application did to the SWD pins is irrelevant.
3. Connect with OpenOCD and mass-erase:
   `-c "init; reset halt; stm32f1x mass_erase 0; shutdown"`
4. BOOT0 back to 0, power-cycle, flash normally.
