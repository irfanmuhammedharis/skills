---
name: circuit-diagram
description: 'Draw high-precision Fritzing/breadboard-style circuit and wiring diagrams as SVG with zero mistakes. Use when the user asks to draw or create a circuit diagram, wiring diagram, breadboard layout, Fritzing-style view, schematic, pin connection diagram, or wants an Arduino/ESP/electronics hookup diagram verified for correctness (wrong pins, missing wires, dangling wires, clipped labels, LED polarity, pull-ups, relay/buzzer polarity). Produces a pin-accurate wiring table (JSON spec), a breadboard-style SVG, and runs an automated checker that fails on any wiring error.'
---

# High-Precision Circuit Diagrams

Draw **Fritzing-style breadboard diagrams** (parts placed physically on a real breadboard) that are *pin-accurate and mistake-free*, backed by an automated verification gate.

## When to Use
- User asks for a circuit/wiring/hookup/breadboard/Fritzing diagram
- Wiring for Arduino, ESP32, STM32, Raspberry Pi or any breadboard project
- Any "wire this up" request where wrong pins would break the build
- Reviewing or verifying an existing wiring diagram

## Non-Goals
- Not for PCB layout / KiCad / Eagle autorouting (use dedicated tools)
- Not for pure-logic schematics without a physical breadboard (still possible, but the template targets breadboard builds)

## Core Principles (why diagrams here are never "approximate")

1. **The wiring table is the source of truth.** Write the JSON spec (every wire: `from` → `to`, color, note) *before* drawing. The diagram must always be regenerated/checked against it — never the other way around.
2. **One geometry source.** Pin/hole coordinates come from `scripts/make_breadboard_template.py`, never hard-coded by hand in each diagram. Edit the script to change geometry, then regenerate.
3. **Fixed color code** (matches the legend in the template):
   - Red `#e53935` = 5V / power · Black `#37474f` = GND
   - Orange `#fb8c00` = signal · Green `#43a047` = analog / I2C · Blue `#1e88e5` = other
4. **Label everything.** Every component gets a label (`R1 220Ω`, `LED1`, `U1 L293D`). A wire without a documented purpose is a bug waiting to happen.
5. **Verify or it doesn't ship.** A diagram is only "done" when `verify_diagram.py` exits 0 with the spec and code.

## Procedure

### 1. Gather requirements
Collect: MCU + board, every component, each pin used, power rails, and the code that will drive it. If any pin is unknown, ask — never assume hardware.

### 2. Build the wiring table (JSON spec)
List **every drawn wire** exactly. Reference names: pins by template id (`D13`, `A0`, `GND`, `GND2`, `GND3`, `5V`, `3V3`, `VIN`, `AREF`, `RESET`), holes as `e1`/`f3` (row+column), rails as `-rail` / `+rail`.

```json
{
  "wires": [
    {"from": "D13", "to": "e1", "color": "#fb8c00", "note": "signal into resistor"},
    {"from": "f3", "to": "-rail", "color": "#37474f", "note": "LED cathode"},
    {"from": "-rail", "to": "GND", "color": "#37474f", "note": "ground return"}
  ],
  "labels": ["R1 220Ω", "LED1"]
}
```

### 3. Electrical correctness gate
Run the checklist in [references/electrical-correctness-checklist.md](./references/electrical-correctness-checklist.md) **before drawing**. It catches the classic silent killers: LED polarity/resistor, servo wiring, button pull-ups, relay and buzzer polarity, sensor pull-ups, I2C pins, power/GND shorts.

### 4. Draw the diagram from the template
- Start from [assets/arduino-uno-breadboard-template.svg](./assets/arduino-uno-breadboard-template.svg), or regenerate it:
  `python3 scripts/make_breadboard_template.py`
- Follow [references/breadboard-layout-rules.md](./references/breadboard-layout-rules.md): rails carry power/GND, components straddle the center gutter (LEDs, ICs), resistors/buttons sit within one row half, sensors hang on the edges.
- Put components in `<g id="components">` and wires in `<g id="wires">`. Wire endpoints **must** land exactly on pin/hole centers or rails. Use the color code. Label every component.
- Do **not** hand-edit pin/hole coordinates — reference them via the generator's `pin_xy()` / `hole_xy()` helpers when building the SVG programmatically.

### 5. Verify (mandatory — no skipping)
```bash
python3 scripts/verify_diagram.py --svg diagram.svg --spec wiring.json --code sketch.ino
```
The checker reports and FAILS on:
- **Clipped labels** (text outside the viewBox)
- **Dangling wires** (end not on a pin/hole/rail/junction)
- **Missing wires** (spec says it, diagram doesn't have it)
- **Orphan refs** (spec names a pin/hole/rail the SVG lacks)
- **Wrong color** and **extra wires** (warnings)
- **Code mismatch** (pin numbers in the sketch that the wiring doesn't wire)

Iterate until `RESULT: PASS` (exit 0). A diagram with `FAIL` is **not** deliverable.

### 6. Regenerate assets after geometry changes
If you change the template geometry (rows, columns, board size), update the constants at the top of `scripts/make_breadboard_template.py`, regenerate, and re-run the whole test suite:
```bash
python3 scripts/make_breadboard_template.py --example
python3 tests/test_checker.py
```

## Quality Gates (all must be true)
- [ ] Wiring JSON exists and every drawn wire is listed with `from`, `to`, `color`, `note`
- [ ] Electrical checklist passed (LED, servo, pull-ups, relay/buzzer polarity, rails)
- [ ] Every component is labeled; every label is inside the viewBox
- [ ] Every wire end is on a pin, hole, or rail — nothing dangles
- [ ] `verify_diagram.py` exits 0 for the diagram + spec + code
- [ ] The code that goes with the diagram compiles (Arduino sketch — see the stub-toolchain note below)
- [ ] Wires follow the color code; power uses rails, not random holes

> **Code compile gate (optional but recommended):** verify the Arduino sketch itself compiles by stubbing the Arduino API (declare `digitalWrite`, `pinMode`, `delay`, `Servo`, etc.) and running `g++ -fsyntax-only -Wall -Wextra`. A diagram is only correct if the code it documents actually builds.

## Resources
- [scripts/make_breadboard_template.py](./scripts/make_breadboard_template.py) — Arduino UNO + breadboard generator (single source of truth for all coordinates); `--example` also emits the worked example
- [scripts/verify_diagram.py](./scripts/verify_diagram.py) — the automated correctness gate
- [tests/test_checker.py](./tests/test_checker.py) — self-test that proves the checker catches mistakes
- [assets/arduino-uno-breadboard-template.svg](./assets/arduino-uno-breadboard-template.svg) — ready-to-use blank template
- [examples/led-blink-breadboard.svg](./examples/led-blink-breadboard.svg) + [wiring.json](./examples/led-blink-wiring.json) + [.ino](./examples/led-blink.ino) — worked example that passes all checks
- [references/breadboard-layout-rules.md](./references/breadboard-layout-rules.md) — how parts sit on a breadboard
- [references/electrical-correctness-checklist.md](./references/electrical-correctness-checklist.md) — the anti-mistake electrical rules
