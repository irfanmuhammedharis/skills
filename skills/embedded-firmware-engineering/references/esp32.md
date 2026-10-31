# ESP32 Family (ESP32, S2, S3, C3, C6) — ESP-IDF and Arduino Core

## Contents
1. Variant selection
2. ESP-IDF architecture essentials
3. Critical gotchas (the flaws that bite)
4. Wi-Fi + BLE production patterns
5. OTA and partitions
6. Power management
7. Arduino-core-on-ESP32 notes

---

## 1. Variant Selection

| Variant | Core | Radio | Use when |
|---|---|---|---|
| ESP32 (classic) | Dual Xtensa LX6 | Wi-Fi + BT Classic + BLE | Legacy, BT Classic needed |
| ESP32-S3 | Dual Xtensa LX7 | Wi-Fi + BLE 5 | Default for new Wi-Fi designs; USB OTG, AI vector instructions, more GPIO |
| ESP32-C3 | Single RISC-V | Wi-Fi + BLE 5 | Cost-sensitive, simpler |
| ESP32-C6 | RISC-V | Wi-Fi 6 + BLE 5 + 802.15.4 | Thread/Zigbee + Wi-Fi combos |
| ESP32-S2 | Single Xtensa | Wi-Fi only | USB needed, no BLE |
| ESP32-H2 | RISC-V | BLE + 802.15.4 | Thread/Zigbee only, no Wi-Fi |

Check module vs. chip: use pre-certified modules (WROOM/WROVER/C3-MINI) unless volume justifies chip-down + certification. PSRAM (WROVER, S3-N8R8) only if the application needs it — PSRAM adds latency and power.

## 2. ESP-IDF Architecture Essentials

- ESP-IDF = FreeRTOS + lwIP + Bluetooth stack + drivers, component-based build on CMake. Pin the IDF version per project (`idf.py --version` documented; use release branches, not master).
- Task model: app tasks + system tasks (wifi, bt, lwIP, idle per core). Pin CPU-heavy tasks to a specific core (`xTaskCreatePinnedToCore`); Wi-Fi/BLE stack tasks run on core 0 by default — put real-time work on core 1.
- Interrupt allocation: use `esp_intr_alloc` flags correctly; IRAM-safe ISRs (`IRAM_ATTR`) required if the handler must run during flash operations — a non-IRAM ISR during flash write/erase crashes the chip.
- Logging: `ESP_LOGx` with per-tag levels; set production log level explicitly; route crash logs to flash for field retrieval (core dump partition or esp-coredump to UART).
- `sdkconfig`: treat as source — commit it, diff it between builds, document every non-default setting.

## 3. Critical Gotchas (the flaws that bite)

- **Brown-out on TX**: Wi-Fi TX bursts draw 350–500 mA; insufficient bulk capacitance or weak PSU → brown-out resets that look random. Add ≥10 µF + 100 nF near the module, use a PSU rated ≥1 A peak; keep the brown-out detector enabled (never disable it to "fix" resets — fix the power).
- **Flash wear + power-loss**: NVS is wear-leveled but not transactional against all power cuts; for critical config use NVS with versioned keys + validation, or littlefs/FATFS with power-fail-safe write patterns. Test by power-cycling during writes.
- **Strapping pins**: GPIO0/2/5/12(MTDI)/15(MTDO) on classic (S3/C3 differ) affect boot mode — using them for external circuits without checking boot strapping causes boards that don't boot. Always consult the strapping pin table before pin assignment.
- **ADC2 unusable during Wi-Fi** (classic ESP32): ADC2 conflicts with Wi-Fi radio. Use ADC1 channels, or an external ADC, when Wi-Fi is active.
- **ADC nonlinearity**: ESP32 ADC needs `esp_adc_cal` characterization; raw counts are notably nonlinear at the rails — use the calibration API and state achieved accuracy.
- **Cache-disabled panic**: any code/data in flash is inaccessible during flash erase/write — keep flash operations out of high-rate paths; use `IRAM_ATTR` for anything that must run concurrently.
- **GPIO matrix vs. IO_MUX**: high-speed signals (SPI >40 MHz, RMT, I2S) must use IO_MUX pins, not the GPIO matrix.
- **Stack sizes**: default Arduino/IDF task stacks overflow with printf-heavy code — measure with `uxTaskGetStackHighWaterMark`, enable `CONFIG_FREERTOS_CHECK_STACKOVERFLOW`.

## 4. Wi-Fi + BLE Production Patterns

- Wi-Fi event handling: use the event loop (`esp_event`), never poll status. Reconnect policy: exponential backoff (start 1 s, cap 5 min, ±20% jitter), and after N failures escalate (restart Wi-Fi driver → restart system → fall back to provisioning mode).
- Store credentials in NVS via a provisioning component (`wifi_provisioning` with BLE or SoftAP transport + proof-of-possession); never hardcode.
- BLE: choose Bluedroid (full-featured) or NimBLE (lighter, recommended for new designs); configure coexistence (`CONFIG_SW_COEXIST_ENABLE`) when Wi-Fi+BLE run together — expect BLE latency spikes during Wi-Fi TX; verify BLE notify throughput under Wi-Fi load.
- Watch the `wifi` task priority: starving it causes disconnects that look like network problems. Never block core 0.
- TLS: use `esp-tls` with CA bundle (`esp_crt_bundle_attach`); validate certificates — skipping verification on a WAN device is a fleet compromise waiting to happen.

## 5. OTA and Partitions

- Partition table: define explicitly (`partitions.csv`): factory/OTA_0/OTA_1 + nvs + phy_init + (optional) littlefs/coredump. Never use the default single-OTA layout for products.
- Use `esp_https_ota` with server cert validation; after update, the app must call `esp_ota_mark_app_valid_cancel_rollback()` only after self-tests pass (Wi-Fi connect, sensor check) — otherwise it auto-rolls-back on next boot. Test: kill power mid-download, mid-verify, mid-first-boot.
- Enable flash encryption + secure boot v2 for production (`idf.py` security features) — this changes the flashing workflow; document the production flashing procedure before enabling.
- Anti-rollback: `CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK` with secure version counter.

## 6. Power Management

- Modem sleep (DTIM) for connected-idle devices: ~10–20 mA average vs. ~80 mA without; light-sleep for wake-on-event; deep-sleep (~10 µA, ULP/RTC domain only) for battery devices.
- Deep-sleep state: only RTC memory persists (`RTC_DATA_ATTR`); design boot flow to distinguish cold boot vs. deep-sleep wake (`esp_sleep_get_wakeup_cause`) and skip re-init where valid.
- ULP coprocessor (RISC-V ULP on S3/C3) for sensor sampling during sleep — complex; justify against simply waking the main CPU.
- Measure: sleep current on the final board is often 10–100× datasheet due to devkit USB-UART chips, LDOs, and LEDs — measure on production hardware, not devkits.

## 7. Arduino-Core-on-ESP32 Notes

- Arduino core is a wrapper over ESP-IDF — you can call IDF APIs directly from Arduino sketches; do so for NVS, OTA, and power management rather than re-inventing.
- `loop()` runs as a task (core 1, priority 1); Wi-Fi runs on core 0 — long blocking code in `loop()` degrades but doesn't kill Wi-Fi; long blocking code in a high-priority task will.
- Use `Preferences` (NVS wrapper) not `EEPROM` emulation for new code.
- `esp_task_wdt` is enabled in recent cores — a `loop()` that never yields trips it; structure code non-blocking.
