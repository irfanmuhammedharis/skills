# Raspberry Pi: RP2040/RP2350 (Pico) and Linux SBCs in Embedded Systems

## Contents
1. RP2040/RP2350 (Pico) — microcontroller use
2. PIO — the killer feature
3. Pico traps and failure modes
4. Raspberry Pi (Linux SBC) in embedded products
5. Linux-side rules for reliability
6. MCU + SBC hybrid architectures

---

## 1. RP2040/RP2350 (Pico) — Microcontroller Use

- RP2040: dual Cortex-M0+ @ 133 MHz, 264 KB RAM, **no internal flash** — boots from external QSPI flash (XIP). RP2350: M33 or RISC-V cores, more RAM, TrustZone option.
- Toolchain: Pico SDK (CMake + GCC, C/C++) or MicroPython/CircuitPython; Arduino core exists (arduino-pico) for prototyping. Pico SDK is the production path.
- No EEPROM/flash filesystem by default: reserve flash regions (via linker or `PICO_FLASH_SIZE_BYTES`) for config; wear is on the external flash — plan a filesystem (littlefs) or wear-aware kv-store for frequent writes.
- Boot: ROM bootloader → UF2 drag-and-drop for dev; production flashing via SWD (Picoprobe/debug probe) or custom bootloader over UART/USB.
- Dual core: core 1 must be launched explicitly (`multicore_launch_core1`); shared data needs critical sections/spinlocks; both cores share the XIP flash — heavy flash access stalls both.

## 2. PIO — the Killer Feature

- PIO = programmable I/O state machines (2 blocks × 4 SMs on RP2040) that bit-bang custom protocols cycle-exact, independent of CPU: WS2812/NeoPixel, DMX, custom SPI variants, quadrature encoders, VGA, software UARTs/I2S, high-rate ADC capture.
- Use PIO whenever a protocol has tight timing that would otherwise burn a core or demand ISRs with impossible latency budgets.
- PIO programs are written in PIO assembly (`pioasm`); test them standalone (the SDK has PIO examples; logic-analyzer-verify the timing).
- DMA + PIO pairing: stream data to/from PIO FIFOs via DMA — CPU-free data movement; handle FIFO under/overrun IRQs.

## 3. Pico Traps and Failure Modes

- **External flash dependency**: QSPI layout and quality matter; XIP latency affects ISRs — time-critical code goes in RAM (`__not_in_flash_func`); flash erase stalls everything (same rule as all single-flash MCUs).
- **No hardware brown-out or RTC on RP2040**: add external supervisor/RTC if the product needs them; RP2350 improves this.
- **USB**: TinyUSB stack — composite devices work; respect 1 ms SOF timing, don't block in USB callbacks.
- **3.3 V only, not 5 V tolerant** — level-shift everything from 5 V domains.
- **ADC is mediocre** (DNL issues, ~9 ENOB): for precision analog use an external ADC.
- **Watchdog**: enable (`watchdog_enable`); scratch registers survive watchdog reset — use them to pass reset-cause/diagnostics across the reboot.

## 4. Raspberry Pi (Linux SBC) in Embedded Products

Appropriate roles: gateway, edge ML inference, HMI, protocol bridge — not hard real-time control (Linux kernel latency is unbounded without PREEMPT_RT, and even then it's ms-class).
- Use the Compute Module (CM4/CM5) for products, not the consumer board: eMMC instead of SD, proper thermal design, IO board control.
- SD-card-based Pi in a product = guaranteed field failures: SD corruption from power cuts. Mitigate: read-only rootfs + overlayfs, separate data partition with journaling, or move to eMMC/CM.
- Power: Pi 4/5 need clean 5 V/3–5 A; voltage dips cause SD corruption and USB dropouts — use a proper PMIC design and undervoltage logging (`vcgencmd get_throttled`).
- Peripherals: UART/I2C/SPI via device tree overlays; the mini-UART (ttyS0) baud drifts with core clock — use PL011 (ttyAMA0) for reliable serial.

## 5. Linux-Side Rules for Reliability

- **Read-only or resilient filesystem**: the #1 Pi field failure is filesystem corruption from uncontrolled power loss. Read-only rootfs, tmpfs for /var/log, data partition with f2fs/ext4-journal, or an industrial SLC eMMC.
- **Watchdog**: enable the BCM hardware watchdog (`/dev/watchdog` + watchdog daemon) — reboots a hung Pi; test it by actually hanging the system.
- **Service supervision**: run the application under systemd with `Restart=always`, start-limit, and dependency ordering; log via journald with size caps.
- **Graceful shutdown**: if power can be cut, add a UPS HAT/supercap + GPIO power-fail signal that triggers `shutdown` within the hold-up time; otherwise accept corruption risk and design the filesystem for it.
- **OTA/fleet updates**: use a proven updater (RAUC, Mender, SWUpdate) with A/B partitions — never `apt upgrade` a fleet.
- **Thermal**: Pi throttles at 85 °C; monitor `vcgencmd measure_temp` and log throttle events; design enclosure thermals for worst case.
- **Security**: change default credentials, disable password SSH (keys only), lock down unused services, firewall the WAN side; sign updates.

## 6. MCU + SBC Hybrid Architectures

Best-practice split for IoT products: MCU (Pico/STM32/ESP32) does real-time sensing/control and power management; Pi does connectivity, storage, ML, and UI.
- Inter-processor link: UART (with framed protocol + CRC — see communication-protocols.md §1) or SPI (MCU as slave); define the ICD: command set, versioning, flow control, error handling.
- Power orchestration: MCU controls Pi power (load switch), wakes on events, boots Pi only when needed — cuts system power 10–50× for battery/hybrid devices; MCU supervises Pi watchdog and force-cycles it.
- Firmware update path: Pi updates MCU firmware over the link (define the MCU bootloader protocol; verify + rollback as always).
- Failure isolation: MCU must keep safe-state control running if the Pi crashes — never route safety-critical control through Linux.
