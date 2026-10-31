# Breadboard Layout Rules (Fritzing-style)

How components physically sit on the breadboard in this template. These rules keep
diagrams readable AND buildable — a kid (or robot) can reproduce them from the picture.

## The Breadboard Anatomy (this template)

```
  +------------------------------+      +------------------------------+
  |  + rail (red)                |      |  + rail (red)                |   <- + rail (5V)
  | 1 2 3 4 5 6 7 8              |      | 9 10 11 12 13 14 15 16       |
  | a o o o o o o o o   GUTTER   |      | a o o o o o o o o            |
  | b o o o o o o o o            |      | b o o o o o o o o            |
  | c o o o o o o o o            |      | c o o o o o o o o            |
  | d o o o o o o o o            |      | d o o o o o o o o            |
  | e o o o o o o o o            |      | e o o o o o o o o            |
  |   ======================     |      |   ======================     |  <- center gutter
  | f o o o o o o o o            |      | f o o o o o o o o            |     (DIP ICs, LEDs
  | g o o o o o o o o            |      | g o o o o o o o o            |      straddle here)
  | h o o o o o o o o            |      | h o o o o o o o o            |
  | i o o o o o o o o            |      | i o o o o o o o o            |
  | j o o o o o o o o            |      | j o o o o o o o o            |
  |  - rail (blue)               |      |  - rail (blue)               |   <- - rail (GND)
  +------------------------------+      +------------------------------+
```

- **Rails**: the long red (`+`/5V) and blue (`−`/GND) strips. Power and ground should
  travel on the rails, not through random holes.
- **Rows a–e** and **f–j** are each internally connected horizontally (per column
  group). A hole connects to its 4 neighbours in the same row, same side.
- **Center gutter** (between rows e and f): the two halves are **not** connected —
  this is where DIP ICs and LEDs straddle (one leg above, one below).

## Placement Rules

| Component | How to place it |
|-----------|-----------------|
| **LED** | Straddle the center gutter: anode in a row **a–e**, cathode in row **f–j**, **same column**. Long leg (anode) faces the resistor/D13 side. |
| **Resistor** | Two legs in **two different columns of the same row half** (e.g., row e, cols 1→3), or one leg in a row and the other to a rail. |
| **DIP IC** (e.g., L293D, op-amp) | Across the center gutter: pins 1–4 in row e, pins 5–8 in row f (or the 4×2 pattern), straddling rows e/f in the same columns. |
| **Push button** | Span two columns in the same row half (legs on opposite sides of the button body). |
| **Sensor/display modules** (HC-SR04, DHT11, LCD, MQ3, HC-05, PIR, relay) | Connect with **male–female jumper wires** from their header pins to breadboard holes or rails. Draw the module as a labeled box near the breadboard edge. |
| **Servo / motors** | Do **not** plug directly into the breadboard — they draw too much current. Draw them off-board with wires to the breadboard (signal) and rails (power). |

## Wiring Conventions

1. **Power** (red) and **ground** (black) first, then signals. Draw them on separate
   "lanes" so they don't cross.
2. Wires **may cross** in the picture — add a note that crossings don't touch
   (real wires are stacked). Minimize crossings anyway.
3. Every wire endpoint lands exactly on a **pin center, hole center, or rail**.
   No floating ends. No "almost touching".
4. Route along rows/rails where possible (straight lines), not chaotic diagonals.
5. Component labels go *above* the component, in a contrasting color, e.g. `R1 220Ω`,
   `LED1`, `U1 L293D`, `HC-SR04`.

## Multi-part Projects

For big builds (robots, home automation), the template canvas (1280×700) fits one
MCU + one breadboard. If you need a second breadboard, duplicate the breadboard
group and offset it in `make_breadboard_template.py` — keep coordinates in the script,
never hand-paste.

## Anti-patterns

- ❌ Plugging the LED anode and cathode in the **same row** (shorts the LED)
- ❌ Both legs of a component in the **same column group** (shorts them)
- ❌ Routing 5V through the blue `−` rail
- ❌ Drawing a wire that "looks" connected but misses the pin by a few pixels
- ❌ Hard-coding coordinates that don't match `make_breadboard_template.py`
