# Custom Design Rules (`.kicad_dru`)

Custom rules turn design intent into something the tool enforces. Anything you would otherwise
check by eye in review belongs here.

## Contents
1. Syntax and evaluation model
2. Constraint types
3. Expression grammar and functions
4. Rule cookbook
5. Practice: writing, testing, maintaining

---

## 1. Syntax and Evaluation Model

Rules live in `<project>.kicad_dru` (Board Setup → Design Rules → Custom Rules, or the file
directly). KiCad 10 also has a graphical rule editor that emits the same language, so rules
started in the GUI stay editable as text.

```
(version 1)

(rule <name>
  (constraint <type> <args>)      ; one or more
  (condition "<expression>")      ; optional; omitted = applies to everything
  (layer "<layer_name>")          ; optional; also 'outer' / 'inner'
  (severity error|warning|ignore|exclusion))   ; optional
```

- `(version 1)` must be the first clause in the file.
- **Rules are evaluated in order and the last matching rule wins** for a given constraint type,
  so order from general to specific. Once a matching rule is found for that constraint, earlier
  ones are not consulted.
- Board Setup **Constraints** minima are absolute: a custom rule can only make things *more*
  restrictive than the board minimum, never less. Set board minima to the fab floor.
- `A` = first item under test, `B` = second (binary checks), `L` = layer under test.
- Numeric values take units (`mm`, `in`, `mil`; time units such as `ps` where the constraint is
  time-domain in KiCad 10) and accept simple arithmetic: `(min "1.5mm + 2.0mm")`.
- `#` starts a comment. Use the **Check Rule Syntax** button — a file with any syntax error means
  *no* custom rules are applied at all, silently weakening the whole DRC.

## 2. Constraint Types

| Constraint | Args | What it checks |
|---|---|---|
| `clearance` | min | Electrical clearance between copper of *different* nets (negative min allows overlap) |
| `physical_clearance` | min | Clearance between any two objects on a layer regardless of net (slow; use `clearance` when possible) |
| `hole_clearance` | min | Drilled hole to copper of another net |
| `physical_hole_clearance` | min | Drilled hole to any object regardless of net ("drilling tolerance") |
| `hole_to_hole` | min | Between mechanically drilled holes (protects drill bits) |
| `hole_size` | min/max | Hole diameter; oval holes test minor/major |
| `annular_width` | min/opt/max | Via annular ring |
| `track_width` | min/opt/max | Track and arc width |
| `connection_width` | min | Narrowest copper connecting to a pad/zone (necks in pours) |
| `via_count` | max | Vias per matched net |
| `via_diameter` | min/opt/max | Via pad diameter |
| `edge_clearance` | min/opt/max | Object to board edge (milling tolerance) |
| `courtyard_clearance` | min | Footprint courtyard overlap |
| `silk_clearance` | min/opt/max | Silkscreen to other objects |
| `text_height` / `text_thickness` | min/opt/max | Legibility of printed text |
| `diff_pair_gap` | min/opt/max | Gap on coupled sections |
| `diff_pair_uncoupled` | max | Length routed uncoupled |
| `length` | min/max | Total routed length per matched net (time units in KiCad 10 time-domain mode) |
| `skew` | max | Deviation of each matched net from the group average |
| `creepage` | min | Creepage distance (KiCad 9+); the safety-critical companion to clearance |
| `thermal_relief_gap` | min | Gap between pad and zone on a thermal connection |
| `thermal_spoke_width` | opt | Spoke width on thermal connections |
| `min_resolved_spokes` | min | Required number of connected thermal spokes |
| `zone_connection` | `solid`/`thermal_reliefs`/`none` | How zones attach to matched pads |
| `disallow` | `track via micro_via buried_via pad zone text graphic hole footprint` | Keepout-style prohibition |
| `assertion` | `"<expression>"` | Arbitrary invariant must hold |

## 3. Expression Grammar and Functions

Properties: `A.Type`, `A.Net`, `A.NetName`, `A.NetClass`, `A.Layer`, `A.Reference`, `A.Value`,
`A.Width`, `A.Line_Width`, `A.Hole_Size_X` / `_Y`, `A.Pad_Type`, `A.Via_Type`, `A.Name` (zones),
`A.Fabrication_Property`, `A.Soldermask_Margin_Override`, `A.Size_X`/`Size_Y`.
Operators: `==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`, `!`, parentheses. All string parameters
support `*` and `?` wildcards.

Functions (all take wildcards):

| Function | Meaning |
|---|---|
| `A.hasNetclass('<class>')` | Net belongs to the class — **preferred** over `A.NetClass ==` (nets can hold several classes) |
| `A.intersectsCourtyard('<ref>')` / `intersectsFrontCourtyard` / `intersectsBackCourtyard` | Any part of A inside that footprint's courtyard |
| `A.intersectsArea('<zone name>')` | Any part of A inside a zone/rule-area outline |
| `A.enclosedByArea('<zone name>')` | All of A inside it (more expensive) |
| `A.existsOnLayer('<layer>')` | A is present on that layer (independent of the layer being tested) |
| `A.inDiffPair('<base net>')` | A is in `<base>_P`/`_N`; `inDiffPair('*')` = any pair |
| `AB.isCoupledDiffPair()` | A and B are the two halves of one pair |
| `A.memberOfGroup('<group>')` | Group membership, including nested |
| `A.memberOfFootprint('<ref>|<fpid>')` | Belongs to that footprint (an fpid must contain `:`) |
| `A.memberOfSheet('<sheet path>')` | Item's schematic sheet — the bridge from schematic structure to layout rules |
| `A.isPlated()` | Plated hole |
| `A.getField('<field>')` | Footprint field value (footprints only) |

## 4. Rule Cookbook

Copy from [../assets/rules/](../assets/rules/) and adapt. Highlights:

```lisp
# Mains isolation: enforce creepage and clearance across the barrier
(rule mains_creepage
  (constraint creepage (min 6.4mm))
  (condition "A.hasNetclass('MAINS') && !B.hasNetclass('MAINS')"))

(rule mains_clearance
  (constraint clearance (min 3.2mm))
  (condition "A.hasNetclass('MAINS') && !B.hasNetclass('MAINS')"))

# Neck down inside a fine-pitch part, full rules everywhere else
(rule BGA_neckdown
  (constraint track_width (min 0.1mm) (opt 0.13mm))
  (constraint clearance (min 0.1mm))
  (condition "A.intersectsCourtyard('U1')"))

# High current: enforce copper width including pour necks
(rule high_current
  (constraint track_width (min 1.5mm))
  (constraint connection_width (min 1.2mm))
  (condition "A.hasNetclass('HighCurrent')"))

# Keep everything out of the antenna region (draw a rule area named 'ANT_KEEPOUT')
(rule antenna_keepout
  (constraint disallow track via zone pad footprint)
  (condition "A.intersectsArea('ANT_KEEPOUT')"))

# RF: wide clearance around 50 ohm nets, and force the calculated width
(rule rf_width
  (constraint track_width (min 0.34mm) (max 0.38mm))
  (condition "A.hasNetclass('RF50')"))
(rule rf_clearance
  (constraint clearance (min 1.0mm))
  (condition "A.hasNetclass('RF50') && !B.hasNetclass('RF50')"))

# USB 2.0: coupled gap, uncoupled budget, and skew
(rule usb_dp_gap
  (constraint diff_pair_gap (opt 0.2mm))
  (constraint diff_pair_uncoupled (max 5mm))
  (condition "A.inDiffPair('/USB_D')"))
(rule usb_skew
  (constraint skew (max 0.5mm))
  (condition "A.inDiffPair('/USB_D')"))

# Timing budget in the time domain (KiCad 10, netclass has a tuning profile)
(rule ddr_dq_byte0_skew
  (constraint skew (max 5ps))
  (condition "A.hasNetclass('DDR_DQ0')"))

# Thermal integrity: no thermal reliefs on heatsink pads, full spokes elsewhere
(rule heatsink_pads_solid
  (constraint zone_connection solid)
  (condition "A.Fabrication_Property == 'Heatsink pad'"))
(rule fully_spoked_pads
  (constraint min_resolved_spokes 4))

# Mechanical: keep parts away from the board edge on the front side
(rule front_edge_keepout
  (layer "F.Courtyard")
  (constraint physical_clearance (min 2mm))
  (condition "B.Layer == 'Edge.Cuts'"))

# Catch accidental overrides that silently break the fab data
(rule no_mask_overrides
  (constraint assertion "A.Soldermask_Margin_Override == 0mm")
  (condition "A.Type == 'Pad'"))

# Per-sheet rules: everything from the analog sheet gets extra clearance
(rule analog_sheet_clearance
  (constraint clearance (min 0.3mm))
  (condition "A.memberOfSheet('/analog/')"))

# Fab-specific: forbid via types the process does not offer
(rule no_microvias
  (constraint disallow micro_via buried_via))
```

## 5. Practice: Writing, Testing, Maintaining

- Start from the fab profile in `assets/rules/`, then add project rules. Keep the file ordered:
  fab limits → netclass rules → area/keepout rules → assertions.
- Test each rule by deliberately violating it once and confirming DRC fires. An untested rule
  usually matches nothing — a silent pass is the failure mode to fear.
- `severity ignore` is a legitimate tool for known-good exceptions (e.g. blind-via/microvia
  hole-to-hole when the fab drills before laser), but every ignore carries a comment saying why.
- Rule areas (keepouts) drawn on the board and named give you geometric conditions
  (`intersectsArea('name')`) that are far more readable than coordinate maths.
- Re-run DRC after every rules edit: `kicad-cli pcb drc --schematic-parity --severity-all
  --exit-code-violations --format json -o drc.json board.kicad_pcb` (exit code 5 = violations).
- Rules are project documentation. When a rule encodes a datasheet or standard requirement, cite
  it in the comment: `# IEC 60664-1 PD2 material group IIIa, 230 Vrms working`.
