# Nordic nRF Series (nRF52, nRF53, nRF91) — nRF Connect SDK

## Contents
1. Family selection
2. nRF Connect SDK (NCS) essentials
3. SoftDevice vs. Zephyr Bluetooth
4. BLE production patterns
5. Power management (the reason you chose Nordic)
6. DFU and secure boot
7. Traps and failure modes

---

## 1. Family Selection

| Chip | Core | Radio | Use when |
|---|---|---|---|
| nRF52832 | M4F | BLE | Mature, cheap BLE peripheral |
| nRF52840 | M4F | BLE + 802.15.4 + USB | BLE flagship, Thread/Zigbee, USB needed |
| nRF52833 | M4F | BLE + 802.15.4, high temp | Direction finding, industrial temp |
| nRF5340 | Dual M33 | BLE 5.3 + 802.15.4 | New designs: app core + network core, TrustZone |
| nRF9160/9161 | M33 + modem | LTE-M/NB-IoT + GNSS | Cellular IoT; GNSS integrated |
| nRF52 + Arduino/Adafruit core | — | BLE | Prototyping only — graduate to NCS for products |

## 2. nRF Connect SDK (NCS) Essentials

- NCS = Zephyr RTOS + Nordic modules + MCUboot, built with west + CMake. Pin the NCS version (e.g., v2.x) per project; NCS versions change APIs between releases — upgrading is a task, not a drop-in.
- Build system: `west build -b <board>`; board targets for nRF53/nRF91 split cores (`nrf5340dk_nrf5340_cpuapp` / `_cpunet`).
- Configuration layers (understand all three or nothing works): Kconfig (`prj.conf` — software features), Devicetree overlay (`.overlay` — hardware/pin mapping), and Partition Manager (flash layout with MCUboot). Pin assignments live in devicetree, not `#define`s.
- Logging: Zephyr `LOG_*` macros with deferred logging; configure backends (UART/RTT) and levels per module in `prj.conf`.
- VS Code extension (nRF Connect for VS Code) is the reference IDE; command-line west works fine for CI.

## 3. SoftDevice vs. Zephyr Bluetooth

- Legacy nRF5 SDK uses SoftDevice (binary blob BLE stack). NCS uses Zephyr's open BLE host + Nordic controller. New designs: NCS. SoftDevice knowledge matters only for maintaining legacy products.
- Key SoftDevice-era constraints that still shape thinking: radio timeslots are owned by the stack — long ISRs or flash writes at the wrong time break connections.

## 4. BLE Production Patterns

- Roles: peripheral (sensor device) vs. central (gateway); define connection parameters explicitly — interval (7.5 ms–4 s), slave latency, supervision timeout (must be > (1+latency)×interval×2). State the values in the ICD.
- Throughput: negotiate MTU (default 23 B → 247 B with DLE); use notifications with connection interval tuned to data rate; write-with-response only for commands needing reliability.
- Bonding/security: use `BT_SECURITY_L2`+ for anything with user data; store bonds persistently (Zephyr settings subsystem on flash — mind write wear).
- Advertising: use extended advertising for >31 B payloads; manage advertising restart after disconnect; implement directed advertising for fast reconnect to known centrals where needed.
- nRF5340: BLE runs on the network core — application talks via HCI IPC; firmware updates must update both cores (see §6).
- Test at range edge: PER, reconnection after supervision timeout, behavior during peer's OTA.

## 5. Power Management (the reason you chose Nordic)

- System ON sleep with full RAM retention is the default idle — current in µA range with RTC running; System OFF (~0.4–1 µA) for longest sleep, wake only via GPIO/NFC/reset.
- Configure unused pins to disconnected/analog; a single floating input driven mid-rail costs more than the entire sleep budget.
- HFCLK only runs when needed (radio, some peripherals) — audit `nrf_power` / clock requests; a forgotten HFCLK request = mA instead of µA.
- DC/DC converter: enable (`CONFIG_SOC_DCDC_NRF52X`) for radio efficiency — requires the inductor on the board; verify the hardware has it.
- Measure with PPK2 (Power Profiler Kit II) — Nordic's own tool; measure the actual sleep current and connection-event average, compare to the budget table.
- BLE battery math: average current ≈ (event energy × events/s + sleep current); show this calculation with actual measured event charge.

## 6. DFU and Secure Boot

- MCUboot is the standard bootloader in NCS: signed images (imgtool, ECDSA-P256), swap-using-move or overwrite-only modes, downgrade protection via security counter.
- Flash layout via Partition Manager: MCUboot + primary app + secondary slot + settings/storage. Document the map.
- BLE DFU: MCUmgr + SMP over BLE (nRF Connect Device Manager app for testing); supports image upload, confirm, and reset. Always test: interrupted transfer (resume works), power loss mid-swap (rollback), unsigned image (rejected).
- nRF5340: dual-image update (app core + network core) — update the network core first, validate, then app core; use the provided multi-image DFU flow.
- nRF91: modem firmware and application firmware are separate DFU targets — modem DFU via the application's flash area; document both procedures.
- Production: lock the debug port (APPROTECT/CTRL-AP) after programming; provide an authorized recovery procedure.

## 7. Traps and Failure Modes

- Flash writes (settings, bonds, FDS) stall the CPU ~ms-scale — during a BLE connection event this breaks timing; schedule writes between events or accept connection parameter slack.
- GPIOTE + PPI: use hardware event routing for timing-critical pin reactions; GPIO interrupt latency through Zephyr is not deterministic enough for µs timing.
- Zephyr thread stacks: size via `CONFIG_MAIN_STACK_SIZE` etc. and measure with thread analyzer; overflow = cryptic faults.
- `printk` in ISRs floods and breaks timing — deferred logging only.
- Devicetree vs. reality: if a peripheral "does nothing," first check it's enabled in the overlay (`status = "okay"`) and pinctrl is assigned.
- Regulatory: Nordic modules carry modular approvals — keep the reference antenna/layout (see antenna-rf.md §6).
