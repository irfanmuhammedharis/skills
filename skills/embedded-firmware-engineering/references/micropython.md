# MicroPython and Arduino C++: Managed/Rapid Firmware Done Right

## Contents
1. Where MicroPython fits (and where it doesn't)
2. MicroPython performance discipline
3. MicroPython production architecture
4. MicroPython deployment and OTA
5. Arduino C++ language patterns
6. Graduating prototype code to production

---

## 1. Where MicroPython Fits (and Where It Doesn't)

- Fits: gateways/HMI, sensor hubs with relaxed timing (≥10 ms), business-logic-heavy IoT nodes, education, field-configurable devices, rapid product validation. Ports: ESP32 (best supported), RP2040/RP2350, STM32, nRF52.
- Doesn't fit: hard real-time (<1 ms jitter), tight power budgets (interpreter idle draws mA — light/deep sleep exists but wake cost is higher), safety-relevant control, small flash/RAM parts (<256 KB RAM is painful).
- Rule: real-time path in C (module or PIO/hardware peripheral), policy in Python. If you find yourself fighting the interpreter for timing, that's C's job.

## 2. MicroPython Performance Discipline

- Memory is the constraint: allocation causes GC pauses (ms-scale) — preallocate buffers (`bytearray`, `memoryview`), reuse objects in hot loops, avoid string building in loops (write into buffers; `ustruct.pack_into`).
- `micropython.native` decorator: ~2× speed; `micropython.viper`: near-C for integer code with typed pointers — use for protocol parsers, CRCs, bit-packing.
- Const data: `micropython.const()` for all constants — saves RAM per use.
- Interrupt handlers: use `micropython.schedule()` to defer work out of the ISR; hard IRQ handlers must not allocate (no exceptions, no object creation).
- Measure with `gc.mem_free()`/`micropython.mem_info()` in the test suite; call `gc.collect()` deliberately at idle points to control pause timing; `gc.threshold()` to reduce collection frequency.
- Async: `uasyncio` for concurrent network/sensor loops — one event loop, cooperative tasks; never mix blocking socket calls with uasyncio tasks.

## 3. MicroPython Production Architecture

- Freeze application modules into firmware (`.mpy` or frozen manifest build) — RAM stays free (frozen code runs from flash), boot is fast, and the filesystem holds only config/data.
- Structure like C: `main.py` = thin bootstrap (recovery mode check, watchdog start) → imports app modules; hardware access wrapped in driver classes with `init/deinit`.
- Watchdog: `machine.WDT` fed only by the health supervisor, same policy as C (reliability-testing.md).
- Exceptions: top-level catch-all logs to flash file + resets — an uncaught exception in the field must leave evidence (`sys.print_exception` to a rotated log).
- Recoverability: safe-mode boot (hold button / N failed boots → skip app, run REPL/maintenance mode); `boot.py` checks the flag before starting the app.

## 4. MicroPython Deployment and OTA

- Filesystem: littlefs2 (power-fail safe — the default on modern ports; FAT is not).
- OTA strategy: full firmware image via the port's OTA (ESP32: `esp32.Partition` OTA works from Python) for interpreter+frozen code; config/data updates as files. App-file-only updates are tempting but version-skew with the interpreter — prefer whole-image updates for products.
- Protect the REPL in production: disable UART REPL or gate behind authentication; WebREPL off.
- Versioning: report interpreter version + frozen app version + config version in telemetry.

## 5. Arduino C++ Language Patterns

The arduino.md file covers the platform; this is the language discipline for Arduino sketches that must not crash:

- Classes, not globals: wrap each peripheral in a class with `begin()`/`update()`; the sketch composes objects — testable, multi-instance, clean.
- `String` ban on AVR (heap fragmentation kills after days): fixed `char buf[N]` + `snprintf`; on ESP32/ARM with real RAM, `String` is tolerable but still avoid in hot loops.
- PROGMEM/flash strings: `F("literal")` on AVR; on ESP32 strings live in flash already.
- Non-blocking time: `millis()` subtraction state machines; `elapsedMillis` helper class acceptable; `delay()` allowed only in setup paths.
- Static allocation: declare objects globally or in static storage — avoid `new` except in init.
- Templates lightly: Arduino's compiler supports them, but heavy template metaprogramming explodes compile errors for marginal gain — keep to simple containers.
- Interrupt safety: `volatile` + `noInterrupts()/interrupts()` around multi-byte shared data — same rules as embedded-c.md §2.

## 6. Graduating Prototype Code to Production

Decision gate: product requirements (power, timing, certification, volume) vs. what the managed stack delivers. When graduating:
- MicroPython → C: port drivers first (same class API in C), keep Python for bring-up scripts and manufacturing test (it's excellent there).
- Arduino → native SDK: pin map, state machines, protocol code survive; replace library calls per arduino.md §5.
- Keep MicroPython/Arduino permanently for: manufacturing test fixtures, internal tools, demo units — that's legitimate production use, not a compromise.
