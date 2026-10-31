# Toolchains, IDEs, and Build Systems for Embedded Development

## Contents
1. PlatformIO (the recommended cross-platform build system)
2. Vendor IDEs: STM32CubeIDE, nRF Connect (VS Code), ESP-IDF tools, Arduino IDE 2
3. Compilers: GCC ARM, LLVM/clang, IAR, Keil
4. Debuggers and probes: ST-Link, J-Link, Picoprobe, ESP-Prog
5. CI/CD for firmware
6. RF/wireless development tools (the "RF connect" stack)

---

## 1. PlatformIO

The default choice for multi-platform firmware projects (AVR, ESP32, STM32, nRF52, RP2040, 1000+ boards).

- `platformio.ini` is the single source of truth: platform, board, framework, build flags, library deps (pinned versions), upload/debug config, and **environments** (`[env:debug]`, `[env:release]`, `[env:production]` with different flags).
- Rules for production use:
  - Pin everything: `platform = espressif32@6.x.x`, `lib_deps = owner/lib@1.2.3` — never float versions.
  - Separate environments for debug/release: release sets `-Os`, strips debug, enables watchdog config; debug adds `-Og -g3` and asserts.
  - Use `extra_scripts` for version stamping (git hash → `build_flags`) so every binary reports its origin.
  - `build_unflags` to remove Arduino core defaults that hide warnings.
- Unit testing: `pio test` with Unity on native (host) env for logic + on-target env for drivers — integrate into CI.
- Debugging: PIO Unified Debugger works with ST-Link/J-Link/ESP-Prog; configure `debug_tool` per env.
- Limits: exotic vendor SDKs (full nRF Connect SDK features, ESP-IDF menuconfig depth) eventually outgrow PIO's abstraction — graduate to native toolchains when the project needs them.

## 2. Vendor IDEs

| IDE | Stack | Strengths | Watch-outs |
|---|---|---|---|
| STM32CubeIDE | CubeMX + Eclipse + GCC | .ioc config of record, Fault Analyzer, SWV/ITM trace | Regeneration overwrites non-USER-CODE sections |
| nRF Connect for VS Code | west + Zephyr + Kconfig | Reference NCS environment, devicetree/Kconfig GUIs, PPK2 integration | Steep config layering (Kconfig + devicetree + Partition Manager) |
| ESP-IDF (VS Code ext / Eclipse) | CMake + idf.py | menuconfig, partition tables, core-dump analysis, size analysis (`idf.py size-components`) | sdkconfig drift between machines — commit it |
| Arduino IDE 2 | arduino-cli | Fastest start, education | No version pinning rigor, no tests — prototype only |
| Keil MDK (µVision) | ARMCC/AC6 | Strong optimizer, RTX RTOS, safety certs | Commercial, Windows-only |
| IAR EWARM | IAR compiler | Best-in-class optimization, functional-safety certified editions | Commercial; migration cost from GCC |
| Segger Embedded Studio | GCC/clang + J-Link | Excellent debug experience, free for some Nordic use | — |
| Zephyr west + CMake (CLI) | Zephyr | CI-native, board-agnostic | Manual everything — but fully scriptable |

Rule: pick the vendor-native toolchain for production (deepest hardware support); use PlatformIO for multi-platform projects, rapid prototyping, and test automation.

## 3. Compilers

- **arm-none-eabi-gcc**: the default for Cortex-M. Use `-Os` for release, `-Og` for debug, `-ffunction-sections -fdata-sections + --gc-sections`, LTO only with testing (it exposes latent bugs — good, but budget the time). Always `-Wall -Wextra -Werror` + map file review.
- **clang/LLVM**: increasingly viable (Zephyr supports it); better diagnostics; check vendor HAL compatibility first.
- **ARMCC (Keil)/IAR**: tighter code on some targets, certified compilers for safety-critical (IEC 61508/ISO 26262 workflows) — use when certification requires tool qualification.
- Version-pin the compiler per project; record it in the build notes; a compiler upgrade is a change to the shipped binary — regression-test it.
- Understand your linker script: memory regions, section placement, stack/heap sizing symbols. Never ship with the vendor's default linker layout unreviewed.

## 4. Debuggers and Probes

- **ST-Link** (incl. on Nucleo): STM32 only, cheap, SWD + SWV.
- **J-Link**: universal Cortex-M + RISC-V; RTT (fast bidirectional debug channel over SWD — replace UART printf for timing-sensitive debug), Ozone/SystemView for RTOS-aware tracing. The professional default.
- **Picoprobe / debugprobe**: RP2040/RP2350 SWD; also flashes the Pico itself.
- **ESP-Prog / built-in USB-JTAG** (S3/C3): JTAG debugging + `openocd` for ESP32.
- **Logic analyzer** (Saleae, DSLogic, even a $10 Cypress FX2): non-negotiable for protocol bring-up — verify I2C/SPI/UART timing and framing on the wire before blaming code.
- **Oscilloscope**: power-rail ripple during radio TX, reset behavior, crystal startup, PWM edges.
- **Power profiling**: Nordic PPK2 or Joulescope — sleep-current verification is impossible with a multimeter alone.

## 5. CI/CD for Firmware

- Every commit: build all envs (warnings-as-errors), run host unit tests, archive the `.elf/.hex/.bin` + map file + git hash.
- Nightly: HIL test rig (self-hosted runner with a debug probe + target board): flash, run scripted tests, capture UART logs, report.
- Release pipeline: version bump → signed build (OTA image signing in CI, keys in HSM/secrets, never in repo) → artifacts + changelog → staged rollout hooks.
- Reproducibility: containerized toolchain (Docker image with pinned gcc/SDK versions) so any commit rebuilds bit-identically years later.
- Static analysis in CI: cppcheck/clang-tidy on every PR; MISRA checker if safety-relevant.

## 6. RF/Wireless Development Tools ("RF Connect" stack)

For BLE/RF development and validation:
- **nRF Connect for Desktop**: Bluetooth Low Energy app (GATT browser/server emulator), Programmer (flashing), Power Profiler (PPK2 UI), RSSI Viewer, Direct Test Mode app — the standard BLE dev toolkit.
- **nRF Connect for Mobile** (iOS/Android): field GATT testing, DFU over BLE via nRF Connect Device Manager.
- **Sniffers**: nRF52840 dongle + Wireshark plugin for BLE over-the-air capture; TI Packet Sniffer for sub-GHz/Zigbee; ESP32 Wi-Fi promiscuous capture. Air captures settle protocol disputes instantly.
- **VNA** (NanoVNA for hobby, proper VNA for production): antenna S11 verification — see antenna-rf.md.
- **Spectrum analysis**: TinySA for hobby pre-checks; certified lab gear for compliance.
- **Direct Test Mode (DTM)**: run the radio in continuous TX/RX test modes for PER measurement and pre-compliance — mandatory before claiming RF performance.
- For ESP32: `esp_rf` certification test firmware; for STM32WB/WL: vendor RF test modes. Document the DTM procedure in the production test plan.
