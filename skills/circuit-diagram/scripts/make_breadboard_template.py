#!/usr/bin/env python3
"""Generate a high-precision Fritzing-style breadboard SVG for circuit diagrams.

Produces:
  (default)  assets/arduino-uno-breadboard-template.svg  - blank Arduino UNO + breadboard base
  --example  examples/led-blink-breadboard.svg           - worked example: blinky LED on D13

Design rules encoded here (must match verify_diagram.py):
  * Every MCU pin is a <circle class="pin" id="pin-<NAME>"> with a <text> label.
  * Every breadboard hole is a <circle class="hole" id="hole-<row><col>">.
  * Wires are <path class="wire" ...> or <line class="wire">; endpoints must land on
    a pin/hole center (or another wire end = junction).
  * Color code: red #e53935 = 5V/power, black #37474f = GND, orange #fb8c00 = signal,
    green #43a047 = analog/I2C, blue #1e88e5 = other.

Geometry reference (viewBox 0 0 1280 700):
  Arduino:  x=30..460, y=100..510  (left headers x=46, right digital header x=446)
  Breadboard: x=560..1196, y=100..660
    + rail y=112..124 (red), - rail y=636..648 (blue)
    left block  cols 1-8   x = 590 + 36*(c-1)
    right block cols 9-16  x = 922 + 36*(c-9)
    rows a-j    y = 150 + 30*(r-1)   (horizontal gutter between row e=270 and f=330)
    vertical gutter between col 8 (x=842) and col 9 (x=922)
"""
import sys
import pathlib

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------------------
# Geometry constants (single source of truth - keep in sync with verify script)
# ----------------------------------------------------------------------------
ARDUINO = dict(x=30, y=100, w=430, h=410)
PIN_X_LEFT = 46
PIN_X_RIGHT = 446
PIN_STEP = 22

POWER_NAMES = ("RESET", "3V3", "5V", "GND", "GND2", "VIN")
ANALOG_NAMES = ("A0", "A1", "A2", "A3", "A4", "A5")
DIGITAL_ROW1_NAMES = tuple(f"D{i}" for i in range(8))
DIGITAL_ROW2_NAMES = tuple(f"D{i}" for i in range(8, 14)) + ("GND3", "AREF")

POWER_PINS = [  # (name, color, offset within header) - matches real Uno silkscreen
    ("RESET", "#b0bec5", 0), ("3V3", "#ef5350", 1), ("5V", "#ef5350", 2),
    ("GND", "#455a64", 3), ("GND2", "#455a64", 4), ("VIN", "#b0bec5", 5),
]
ANALOG_PINS = [  # real Uno: A5 at top of the header, A0 at the bottom
    ("A5", "#a5d6a7", 0), ("A4", "#a5d6a7", 1), ("A3", "#a5d6a7", 2),
    ("A2", "#a5d6a7", 3), ("A1", "#a5d6a7", 4), ("A0", "#a5d6a7", 5),
]
DIGITAL_ROW1 = [(f"D{i}", "#ffd166", i) for i in range(8)]
DIGITAL_ROW2 = [(f"D{i}", "#ffd166", i - 8) for i in range(8, 14)] \
    + [("GND3", "#455a64", 6), ("AREF", "#b0bec5", 7)]

BB = dict(x=560, y=100, w=636, h=560)
BB_LEFT_X0 = 590
BB_RIGHT_X0 = 922
BB_COL_STEP = 36
BB_ROW_Y0 = 150
BB_ROW_STEP = 30
BB_ROWS = "abcdefghij"

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def pin_y(header_top, offset):
    return header_top + offset * PIN_STEP


def header_y(name):
    if name in POWER_NAMES:
        return ARDUINO["y"] + 50
    if name in ANALOG_NAMES:
        return ARDUINO["y"] + 186
    if name in DIGITAL_ROW1_NAMES:
        return ARDUINO["y"] + 50
    return ARDUINO["y"] + 226  # D8..D13, GND3, AREF


def hole_xy(row, col):
    col = int(col)
    x = BB_LEFT_X0 + (col - 1) * BB_COL_STEP if col <= 8 else \
        BB_RIGHT_X0 + (col - 9) * BB_COL_STEP
    r = BB_ROWS.index(row)
    if r <= 4:  # rows a-e above the center gutter
        y = BB_ROW_Y0 + r * BB_ROW_STEP
    else:       # rows f-j below the 60px center gutter
        y = BB_ROW_Y0 + 180 + (r - 5) * BB_ROW_STEP
    return x, y


def pin_xy(name):
    if name.startswith("A"):
        x = PIN_X_LEFT
    elif name.startswith("D") or name in ("GND3", "AREF"):
        x = PIN_X_RIGHT
    else:  # RESET, 3V3, 5V, GND, GND2, VIN
        x = PIN_X_LEFT
    off = 0
    for pins, col in ((POWER_PINS, "L"), (ANALOG_PINS, "L"), (DIGITAL_ROW1, "R"), (DIGITAL_ROW2, "R")):
        for nm, _c, i in pins:
            if nm == name:
                off = i
                x = PIN_X_LEFT if col == "L" else PIN_X_RIGHT
                break
    return x, pin_y(header_y(name), off)


def wire(d, color, width=4):
    return f'    <path class="wire" d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n'


def arduino_svg():
    s = []
    s.append(f'    <rect x="{ARDUINO["x"]}" y="{ARDUINO["y"]}" width="{ARDUINO["w"]}" height="{ARDUINO["h"]}" rx="16" fill="#00979d" stroke="#007c8a" stroke-width="2"/>\n')
    s.append(f'    <rect x="{ARDUINO["x"]}" y="{ARDUINO["y"]}" width="{ARDUINO["w"]}" height="46" rx="16" fill="#00838f"/>\n')
    s.append(f'    <text x="{ARDUINO["x"] + ARDUINO["w"] // 2}" y="{ARDUINO["y"] + 31}" text-anchor="middle" font-size="20" font-weight="bold" fill="#fff">Arduino UNO</text>\n')
    # USB connector
    s.append(f'    <rect x="{ARDUINO["x"] + 165}" y="{ARDUINO["y"] - 14}" width="100" height="16" rx="4" fill="#cfd8dc"/>\n')
    # reset button + power jack (decorative)
    s.append(f'    <circle cx="{ARDUINO["x"] + 100}" cy="{ARDUINO["y"] + 12}" r="7" fill="#b0bec5"/>\n')
    s.append(f'    <circle cx="{ARDUINO["x"] + 40}" cy="{ARDUINO["y"] + ARDUINO["h"] - 38}" r="11" fill="#455a64"/>\n')
    # ICSP decorative dots
    for i in range(6):
        sx = ARDUINO["x"] + 250 + (i % 3) * 16
        sy = ARDUINO["y"] + 20 + (i // 3) * 12
        s.append(f'    <circle cx="{sx}" cy="{sy}" r="2.5" fill="#b2dfdb"/>\n')
    # pins
    for name, color, off in POWER_PINS + ANALOG_PINS:
        x = PIN_X_LEFT
        y = pin_y(header_y(name), off)
        disp = "GND" if name == "GND2" else name
        s.append(f'    <g class="pin" id="pin-{name}"><circle cx="{x}" cy="{y}" r="5.5" fill="{color}" stroke="#fff" stroke-width="1.5"/><text x="{x + 14}" y="{y + 4}" font-size="11" font-weight="bold" fill="#fff">{disp}</text></g>\n')
    for name, color, off in DIGITAL_ROW1 + DIGITAL_ROW2:
        x = PIN_X_RIGHT
        y = pin_y(header_y(name), off)
        disp = "GND" if name == "GND3" else name
        s.append(f'    <g class="pin" id="pin-{name}"><circle cx="{x}" cy="{y}" r="5.5" fill="{color}" stroke="#fff" stroke-width="1.5"/><text x="{x - 12}" y="{y + 4}" text-anchor="end" font-size="11" font-weight="bold" fill="#fff">{disp}</text></g>\n')
    return "".join(s)


def breadboard_svg():
    s = []
    s.append(f'    <rect x="{BB["x"]}" y="{BB["y"]}" width="{BB["w"]}" height="{BB["h"]}" rx="10" fill="#fafafa" stroke="#b0bec5" stroke-width="2"/>\n')
    # rails (split at the vertical gutter)
    left_rail_end = BB_LEFT_X0 + 8 * BB_COL_STEP + 30
    right_rail_start = BB_RIGHT_X0 - 30
    s.append(f'    <rect x="{BB["x"] + 12}" y="{BB["y"] + 12}" width="{left_rail_end - (BB["x"] + 12)}" height="12" rx="4" fill="#ff8a80"/>\n')
    s.append(f'    <rect x="{right_rail_start}" y="{BB["y"] + 12}" width="{BB["x"] + BB["w"] - 12 - right_rail_start}" height="12" rx="4" fill="#ff8a80"/>\n')
    s.append(f'    <text x="{BB["x"] + 24}" y="{BB["y"] + 22}" font-size="11" font-weight="bold" fill="#c62828">+</text>\n')
    s.append(f'    <rect x="{BB["x"] + 12}" y="{BB["y"] + BB["h"] - 24}" width="{left_rail_end - (BB["x"] + 12)}" height="12" rx="4" fill="#90a4ae"/>\n')
    s.append(f'    <rect x="{right_rail_start}" y="{BB["y"] + BB["h"] - 24}" width="{BB["x"] + BB["w"] - 12 - right_rail_start}" height="12" rx="4" fill="#90a4ae"/>\n')
    s.append(f'    <text x="{BB["x"] + 24}" y="{BB["y"] + BB["h"] - 14}" font-size="11" font-weight="bold" fill="#37474f">&#8722;</text>\n')
    # holes
    for c in range(1, 17):
        for r, row in enumerate(BB_ROWS):
            x, y = hole_xy(row, c)
            s.append(f'    <circle class="hole" id="hole-{row}{c}" cx="{x}" cy="{y}" r="4.2" fill="#d5dbe4" stroke="#7c8ea0" stroke-width="0.8"/>\n')
    # row letters
    for row in BB_ROWS:
        x, y = hole_xy(row, 1)
        s.append(f'    <text x="{BB["x"] + 16}" y="{y + 4}" font-size="10" fill="#78909c">{row}</text>\n')
    # column numbers
    for c in range(1, 17):
        x, _ = hole_xy("a", c)
        s.append(f'    <text x="{x}" y="{BB["y"] + 40}" text-anchor="middle" font-size="9" fill="#90a4ae">{c}</text>\n')
    return "".join(s)


def legend_svg():
    items = [("#e53935", "5V / power"), ("#37474f", "GND"),
             ("#fb8c00", "signal"), ("#43a047", "analog / I2C"), ("#1e88e5", "other")]
    s = [f'    <rect x="30" y="560" width="430" height="124" rx="10" fill="#fff" stroke="#cfd8dc" stroke-width="2"/>\n',
         f'    <text x="46" y="586" font-size="14" font-weight="bold" fill="#26343f">Wire colors</text>\n']
    for i, (col, label) in enumerate(items):
        ly = 606 + (i // 3) * 24
        lx = 46 + (i % 3) * 140
        s.append(f'    <rect x="{lx}" y="{ly - 8}" width="18" height="10" rx="3" fill="{col}"/>\n')
        s.append(f'    <text x="{lx + 24}" y="{ly}" font-size="11" fill="#26343f">{label}</text>\n')
    return "".join(s)


def template_svg():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 700" '
            f'width="1280" height="700" role="img" aria-label="Arduino UNO breadboard template">\n'
            f'  <!-- Generated by make_breadboard_template.py - edit the script, not this file -->\n'
            f'  <!-- Layers: draw components in <g id="components">, wires in <g id="wires"> -->\n'
            f'  <g id="board">\n{arduino_svg()}{breadboard_svg()}</g>\n'
            f'  <g id="components"></g>\n'
            f'  <g id="wires"></g>\n'
            f'  <g id="legend">\n{legend_svg()}</g>\n'
            f'</svg>\n')


def example_svg():
    """Blinky LED: D13 -> resistor (row e, col1-col3) -> LED anode e3, LED cathode f3
    (straddles the horizontal gutter) -> - rail -> GND pin."""
    # pin/hole coordinates
    d13 = pin_xy("D13")
    gnd = pin_xy("GND")          # power header GND
    e1 = hole_xy("e", 1)
    e3 = hole_xy("e", 3)
    f3 = hole_xy("f", 3)
    rail_x = BB_LEFT_X0          # - rail left end
    rail_y = BB["y"] + BB["h"] - 18

    s = template_svg()
    s = s.replace('<g id="components"></g>',
        '  <g id="components">\n'
        f'    <!-- resistor R1 on row e, cols 1-3 -->\n'
        f'    <line x1="{e1[0]}" y1="{e1[1]}" x2="{e3[0]}" y2="{e3[1]}" stroke="#90a4ae" stroke-width="3"/>\n'
        f'    <rect x="{e1[0] + 18}" y="{e1[1] - 8}" width="{e3[0] - e1[0] - 36}" height="16" rx="4" fill="#b0bec5" stroke="#78909c"/>\n'
        f'    <line x1="{e1[0] + 18}" y1="{e1[1]}" x2="{e3[0] - 18}" y2="{e3[1]}" stroke="#90a4ae" stroke-width="3"/>\n'
        f'    <text x="{(e1[0] + e3[0]) // 2}" y="{e1[1] - 14}" text-anchor="middle" font-size="10" font-weight="bold" fill="#455a64">R1 220&#937;</text>\n'
        f'    <!-- LED1 straddles the center gutter: anode in e3 (D13 side), cathode in f3 -->\n'
        f'    <line x1="{e3[0]}" y1="{e3[1]}" x2="{e3[0]}" y2="{e3[1] + 18}" stroke="#90a4ae" stroke-width="3"/>\n'
        f'    <line x1="{f3[0]}" y1="{f3[1]}" x2="{f3[0]}" y2="{f3[1] - 18}" stroke="#90a4ae" stroke-width="3"/>\n'
        f'    <circle cx="{e3[0]}" cy="{e3[1] + 30}" r="12" fill="#ff5a5f"/>\n'
        f'    <path d="M{e3[0] - 7} {e3[1] + 26} a7 7 0 0 1 10 -1" stroke="#ffebee" stroke-width="2" fill="none"/>\n'
        f'    <text x="{e3[0]}" y="{e3[1] - 14}" text-anchor="middle" font-size="10" font-weight="bold" fill="#b3261e">LED1</text>\n'
        f'    <text x="{f3[0] + 10}" y="{f3[1] + 16}" font-size="9" fill="#37474f">cathode</text>\n'
        '  </g>\n')
    s = s.replace('<g id="wires"></g>',
        '  <g id="wires">\n'
        f'    <!-- D13 -> hole e1 (signal, orange) -->\n'
        f'    {wire(f"M{d13[0]} {d13[1]} Q 520 300 {e1[0]} {e1[1]}", "#fb8c00")}'
        f'    <!-- LED cathode f3 -> - rail (GND, black) -->\n'
        f'    {wire(f"M{f3[0]} {f3[1]} L {f3[0]} {rail_y}", "#37474f")}'
        f'    <!-- - rail -> GND pin (black) -->\n'
        f'    {wire(f"M{rail_x} {rail_y} Q 400 580 {gnd[0]} {gnd[1]}", "#37474f")}'
        '  </g>\n')
    return s


def main():
    out = OUT_DIR / "assets" / "arduino-uno-breadboard-template.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template_svg(), encoding="utf-8")
    print(f"wrote {out}")

    if "--example" in sys.argv:
        ex = OUT_DIR / "examples" / "led-blink-breadboard.svg"
        ex.parent.mkdir(parents=True, exist_ok=True)
        ex.write_text(example_svg(), encoding="utf-8")
        print(f"wrote {ex}")


if __name__ == "__main__":
    main()
