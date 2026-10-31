# Symbols, Footprints, and 3D Models

A wrong footprint is the most expensive mistake in PCB design: it survives every electrical
review and is only discovered at assembly.

## Contents
1. Where to get parts, in order of trust
2. Symbol rules
3. Footprint rules (KLC numbers)
4. Land pattern sizing and IPC density levels
5. Special padstacks
6. 3D models
7. Verification before use

---

## 1. Where to Get Parts, In Order of Trust

1. **Official KiCad libraries** — generated from data, KLC-compliant, STEP models. Default choice.
2. **Manufacturer-supplied KiCad/IPC library** or the datasheet's recommended land pattern,
   built by you.
3. **Generated from IPC rules** (KiCad's footprint wizards, or an IPC-7351 generator) using the
   datasheet's package dimensions.
4. **Third-party** (SnapEDA, Ultra Librarian, Component Search Engine, `JLC2KiCad_lib` /
   `easyeda2kicad` for LCSC parts) — usable, but treat as untrusted input: verify pad
   dimensions, pin numbering, and 3D alignment against the datasheet before it touches a board.

Whatever the source, the part lands in the **project library** with your name on it.

## 2. Symbol Rules

- Pins on a **2.54 mm (100 mil) grid** — off-grid pins cannot be wired cleanly.
- Pin electrical types set correctly (`power_in`, `power_out`, `output`, `bidirectional`,
  `open_collector`, `passive`, `unspecified`, `no_connect`): ERC is only as good as these.
- Arrange pins by *function*, not by physical package order: power top, ground bottom, inputs
  left, outputs right. A symbol that mirrors the package is a symbol nobody can read.
- Multi-unit symbols for multi-channel parts (quad op-amp = 4 units + power unit). Big MCUs and
  FPGAs: split into units by bank/function.
- Default footprint filled in for single-footprint parts; footprint filters set so the assignment
  dialog offers only sane options.
- Value field = the value or part number, not the symbol name; `Datasheet` field = a real URL.

## 3. Footprint Rules (KLC numbers worth memorising)

- **Silkscreen**: 0.12 mm line width (0.10 mm high density, 0.15 mm low density); never over
  pads or exposed copper; must remain visible after assembly; pin-1 marker mandatory and visible;
  ≥0.5 mm clearance to board edge. Small parts (0201-class): 0.25 mm dot for polarity.
- **Courtyard**: 0.05 mm line width, positions rounded to a 0.01 mm grid. Clearance 0.25 mm
  default, 0.15 mm for parts under 1.5 mm, 0.5 mm for connectors and canned capacitors, 1.0 mm
  for BGA/WLCSP. Courtyards must not overlap in a finished layout.
- **Fabrication layer (F.Fab/B.Fab)**: simplified true component outline, 0.10–0.15 mm lines,
  plus `${REFERENCE}` text and pin-1 marking. This is the layer assembly reads — it is not
  optional decoration.
- **Attributes**: SMD footprints must be typed *SMD*, through-hole *Through hole*, mechanical
  items *Unspecified/excluded* — the position (CPL) file depends on this typing.
- **Origin/anchor** at the package centroid for ICs and passives (pin 1 for polarised THT is
  acceptable if consistent) — the anchor is what the pick-and-place machine uses.
- Do not duplicate a footprint to change pin numbering; fix pin mapping in the symbol.
- Multiple pads that are physically one net (thermal pad + pin, split pads) share the same pad
  number.

## 4. Land Pattern Sizing and IPC Density Levels

- IPC-7351 density levels: **Level A (most)** for wave/low-density and hand rework, **Level B
  (nominal)** for most designs — the default, **Level C (least)** for high density and fine
  pitch. Choose per board, not per part, and say which in the design record.
- Chip components: heel/toe/side fillet per level; too-long pads increase tombstoning risk, too
  short reduce solder joint strength. Take the manufacturer's recommended land pattern when it
  exists — they tested it.
- QFN/DFN: use the manufacturer's pattern. Central thermal pad gets a **windowpane** paste
  stencil (typically 50–80% paste coverage split into segments) so the part does not float or
  tombstone on a paste lake, plus a via array to the plane (see power-thermal.md).
- BGA: pad diameter ~80% of ball diameter, NSMD (non-solder-mask-defined) unless the vendor
  says otherwise, and check the fab can hit the resulting trace/space in the escape region
  before committing to the part.
- Connectors and any part with mechanical mating: verify pad *and* hole dimensions against the
  mechanical drawing, including the plated/non-plated distinction for mounting holes.

## 5. Special Padstacks

- **Through-hole**: hole = lead diameter + 0.2…0.3 mm; annular ring ≥ fab minimum (typically
  ≥0.15 mm, JLCPCB standard 0.13 mm for PTH). Oval pads for parts with lead-forming tolerance.
- **Castellated / edge-plated**: needs the fab's specific rules; declare it on the fab notes.
- **Mounting holes**: decide plated vs non-plated deliberately. Plated + connected to GND for
  chassis bonding; non-plated for isolation. Add keep-outs for screw head and washer diameter.
- **Test points**: dedicated test-point footprints (1.0–1.5 mm exposed copper), tagged with the
  `Test point` fabrication property so the test-point report can find them.
- **Solder mask / paste overrides**: only with a written reason; `assertion` rules exist to catch
  accidental overrides (see design-rules-dru.md).
- Via-in-pad requires filled-and-capped vias — a fab option with cost. Never leave an unfilled
  via in a pad and hope.

## 6. 3D Models

- Prefer **STEP** (KiCad 10 official libraries ship STEP only): accurate geometry, correct
  export to mechanical CAD, smaller install.
- Store project models in `lib/3d/`, reference them as `${KIPRJMOD}/lib/3d/part.step`.
- Align model to footprint origin, correct rotation and Z offset; verify in the 3D viewer with
  the board — a model that floats 2 mm high hides an enclosure collision.
- The STEP export of the board is the mechanical hand-off; do it early, not at the end, and give
  it to whoever owns the enclosure.

## 7. Verification Before Use

Run this on every part you or a third party created:

- [ ] Pad dimensions and pitch measured against the datasheet drawing (print at 1:1 and lay the
      part on it for THT/connectors — still the fastest check that exists)
- [ ] Pin numbering matches the datasheet *and* the symbol
- [ ] Courtyard, silkscreen, fab layers present and KLC-conformant
- [ ] Footprint attribute (SMD/THT) and anchor correct
- [ ] 3D model aligned in the 3D viewer
- [ ] Symbol pin types correct; ERC gives no surprises on a test schematic
- [ ] Footprint checker in the Footprint Editor run clean (KiCad flags overlapping pads,
      bad courtyards, mask/paste oddities)
