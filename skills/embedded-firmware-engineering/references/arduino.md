# Arduino Platform (AVR, ARM, ESP cores) — Production Use

## Contents
1. Platform scope and limits
2. AVR (Uno/Nano/Mega) specifics
3. ARM cores (Due, Zero, MKR, Nano 33)
4. Writing reliable Arduino code
5. Moving from Arduino to production
6. Library vetting rules

---

## 1. Platform Scope and Limits

Arduino is a framework, not hardware: the same `setup()/loop()` API runs on AVR (Uno, Nano, Mega), SAMD (MKR, Zero), STM32 (via STM32duino core), ESP32/ESP8266 (via espressif cores), and nRF52 (via Adafruit/Seeed cores). Code portability across cores is partial — verify pin maps, ADC resolution, PWM frequency, and interrupt support per core.

Honest limits: Arduino core hides the clock tree, prioritizes ease over timing accuracy, and many libraries block. Acceptable for prototypes, education, and low-risk products; for anything with safety, power, or volume constraints, treat Arduino code as a prototype to be hardened (see §5).

## 2. AVR (ATmega328P/2560) Specifics

- Resources: 32 KB flash / 2 KB RAM (328P) — RAM exhaustion is the #1 failure. Check free RAM at runtime (`freeMemory()` pattern via stack/heap gap); keep ≥300 B headroom.
- Use `PROGMEM` and `F()` macro for all string literals — strings in RAM kill 328P projects silently.
- `millis()` wraps at ~49.7 days: always use subtraction-based comparisons (`if (millis() - last >= interval)`), never `millis() > deadline`.
- `delay()` blocks everything — replace with non-blocking state machines for anything beyond trivial sketches.
- Serial: `HardwareSerial` buffers are 64 B — bursts beyond that drop bytes silently. Drain or enlarge.
- EEPROM: ~100k write cycles; use wear-leveling or write-on-change; AVR EEPROM writes can corrupt mid-write on brown-out — enable BOD fuse (4.3 V for 5 V boards).
- Watchdog: enable via `wdt_enable()`; the old optiboot/bootloader issue (endless reset on WDTO_15MS) is fixed in modern cores — verify on the actual board.
- PWM: default ~490 Hz (pins 5/6 ~980 Hz) — audible whine on motors/LEDs; change timer prescaler if it matters, documenting side effects (pins 5/6 affect millis via Timer0 — do not touch Timer0 prescaler).

## 3. ARM Cores (SAMD21, STM32duino, nRF52 cores)

- 3.3 V logic — not 5 V tolerant (SAMD); level-shift all 5 V peripherals.
- SAMD21: native USB — USB disconnect during `Serial.print` can block; guard with `if (Serial)`.
- STM32duino: exposes HAL underneath; you can mix Arduino API with direct HAL calls — document when you do.
- Adafruit nRF52 core: runs on SoftDevice — see nrf.md; `delay()` in this core yields to the BLE stack, but timing-critical bit-banging still breaks radio events.
- Interrupts: use `attachInterrupt(digitalPinToInterrupt(pin), ...)`; ISRs must be short — flag-and-return.

## 4. Writing Reliable Arduino Code

- Structure every non-trivial sketch as: pin/config constants → module objects (sensor, comms) with `begin()`/`update()` → super-loop calling non-blocking `update()` methods → watchdog refresh last.
- Avoid `String` class on AVR — heap fragmentation causes crashes after hours/days. Use fixed `char` buffers with `snprintf`.
- Every I2C/SPI sensor `begin()` return must be checked; fail into a defined error state with serial/LED diagnostic, never continue blind.
- Add a watchdog + reset-cause log even in Arduino projects (`wdt.h` on AVR, core-specific elsewhere).
- Pins: define with `constexpr uint8_t PIN_X = n;` at top; never scatter raw pin numbers.
- Time: `millis()`/`micros()` subtraction pattern only; on cores with tickless idle verify millis behavior during sleep.

## 5. Moving from Arduino to Production

Graduation path when the product gets serious:
1. Keep Arduino framework but move to PlatformIO (see toolchains-platformio.md): unit tests (`pio test` with Unity), CI builds, dependency pinning, `build_flags` per environment (debug/release).
2. Replace blocking library calls with non-blocking drivers; add proper error paths.
3. Port to native SDK when you hit: hard timing requirements, power targets Arduino sleep can't meet, memory ceilings, or certification requirements. Targets: ESP-IDF (ESP32), nRF Connect SDK (nRF52), STM32 HAL/LL (STM32), AVR bare metal or avr-libc.
4. Whatever survives: the pin map, state machines, protocol parsers, and test cases — port those, not the library calls.

## 6. Library Vetting Rules

Arduino libraries are the biggest quality risk. Before adopting any library:
- Check maintenance: last commit, open issues, forks. Abandoned library = own the code.
- Read the source for: blocking `while` loops without timeout, dynamic allocation patterns, ISR safety, `delay()` calls.
- Check the license (LGPL/static-linking implications for commercial products).
- Pin exact versions (`platformio.ini` or library manager JSON), never float "latest".
- Test the library's failure paths (sensor disconnected, NACK, garbage data) yourself — most libraries only demo the happy path.
