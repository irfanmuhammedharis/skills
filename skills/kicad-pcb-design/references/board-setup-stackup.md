# Board Setup and Stackup

Everything downstream — impedance, EMI, thermal, DRC, 3D, cost — is decided here, in about
twenty minutes, before any copper is drawn.

## Contents
1. Choosing layer count
2. Stackup patterns
3. Real stackup data (JLCPCB standard)
4. Configuring the physical stackup in KiCad
5. Constraints (board minima)
6. Netclasses
7. Tuning profiles and time-domain setup (KiCad 10)
8. Board outline and origins

---

## 1. Choosing Layer Count

| Use case | Layers | Notes |
|---|---|---|
| Simple, low speed, few ICs, cost critical | 2 | Only with a disciplined ground pour on one side and short loops; expect more effort, not less |
| Anything with an MCU + radio + mixed signal, most products | 4 | The default. SIG / GND / PWR / SIG buys EMI margin, impedance control and debug time |
| Dense BGA, multiple high-speed buses, tight EMC | 6–8 | Adds routing layers with adjacent references |

4-layer at prototype quantities is typically only marginally more expensive than 2-layer and
routinely saves a respin. Justify a 2-layer choice; don't default to it.

## 2. Stackup Patterns

- **4-layer, general product**: `SIG+GND-fill / GND / PWR / SIG+GND-fill`. Signal layers each
  have an adjacent plane; the thin outer prepreg (~0.2 mm) gives tight coupling to the reference.
- **4-layer, high-speed preference**: `SIG / GND / GND / SIG` with power routed as wide tracks
  and local polygons — better return paths than a fragmented power plane.
- Avoid split power planes under fast signals. If splits are unavoidable, keep every fast net's
  entire path over a single unbroken reference.
- Symmetry matters: an asymmetric copper distribution warps during reflow. Balance copper area
  per layer (add non-functional pours/hatching if needed) and keep the stackup mechanically
  symmetric about the centre.
- Assign layers before placement, and write the assignment into the design record:
  which layer carries what, which planes are what net, where the reference for each signal layer
  is.

## 3. Real Stackup Data (JLCPCB Standard, 1.6 mm 4-layer)

`JLC04161H-7628` — the common default:

| Layer | Material | Thickness |
|---|---|---|
| Top copper | Cu | 0.035 mm (1 oz) |
| Prepreg | 7628 ×1 | 0.2104 mm |
| Inner L2 | Cu | 0.0152 mm (0.5 oz) |
| Core | FR-4 | 1.065 mm |
| Inner L3 | Cu | 0.0152 mm |
| Prepreg | 7628 ×1 | 0.2104 mm |
| Bottom copper | Cu | 0.035 mm |

Dielectric constants used by JLCPCB: 7628 ≈ 4.4, 2116 ≈ 4.16, 3313 ≈ 4.1, 1080 ≈ 3.91;
solder mask ≈ 4.6. Alternatives `JLC04161H-3313` (0.0994 mm prepreg, 1.265 mm core) and
`-1080` give thinner outer dielectric — pick the one whose prepreg gives the trace width you
want for your target impedance.

Consequences worth internalising: with 0.2104 mm of 7628 prepreg under a 1 oz outer layer, a
50 Ω single-ended microstrip lands near **0.35–0.38 mm** wide, and a 90 Ω USB differential pair
around **0.30/0.20 mm** (width/gap). Compute for your exact stackup with
`pcb_calc.py microstrip --z0 50 …` and cross-check against the fab's own impedance calculator —
they will fabricate to their numbers, not yours.

Always confirm current values on the fab's capability/impedance page before release; process
options change.

## 4. Configuring the Physical Stackup in KiCad

Board Setup → Board Stackup:

- Enter the *actual* dielectric thicknesses, materials, εr and loss tangent from the fab's
  stackup table. This drives the built-in impedance/delay calculations, the 3D and STEP export,
  and any time-domain tuning.
- Set copper weights per layer (outer 1 oz / inner 0.5 oz is standard; ask for 2 oz only when
  the current calculation demands it — it forces wider minimum traces).
- Set the solder mask and silkscreen colours/thickness if impedance matters (mask over a
  microstrip lowers impedance by a couple of ohms — the fab's calculator accounts for it).
- Name and enable only the layers you use; unused enabled layers produce empty gerbers and
  confuse the fab.
- If the board is impedance-controlled, note it in the fab notes and choose one of the fab's
  named stackups explicitly.

## 5. Constraints (Board Minima)

Set to the fab's process floor — these cannot be relaxed later by netclass or custom rule:

| Constraint | JLCPCB standard (1 oz, 2–4 layer) | Note |
|---|---|---|
| Min clearance | 0.127 mm (5 mil) | 2 oz copper needs ≥0.2 mm |
| Min track width | 0.127 mm (5 mil) | 2 oz: ≥0.2 mm |
| Min annular ring | 0.13 mm | |
| Min via hole / diameter | 0.3 / 0.45 mm | 0.2/0.35 mm possible at extra cost |
| Min through-hole (PTH) | 0.2 mm | |
| Hole to hole | 0.5 mm | different nets |
| Copper to board edge | 0.2 mm (0.3 mm safer) | plane pull-back |
| Silkscreen width / height | 0.15 mm / 1.0 mm | smaller text may not be printed |

Design to comfortable values (e.g. 0.2 mm track / 0.2 mm clearance / 0.3 mm drill) and reserve
the minima for the places that genuinely need them — yield and cost both improve.

Also configure here: copper-to-hole clearance, min connection (thermal spoke) width, microvia
rules if used, silk-over-mask/silk-over-copper checks, and length-tuning defaults.

## 6. Netclasses

Define classes and assign nets by pattern, not one by one:

| Class | Typical members | Track | Clearance | Via | Notes |
|---|---|---|---|---|---|
| Default | signals | 0.2 mm | 0.2 mm | 0.6/0.3 | |
| Power | rails <1 A | 0.5 mm | 0.2 mm | 0.8/0.4 | width from calculation |
| HighCurrent | rails ≥1 A | polygon | 0.3 mm | multiple | never a single via |
| GND | ground | pour | 0.2 mm | 0.6/0.3 | |
| USB / DIFF90 | `USB_D*` | 0.30 mm | 0.2 mm | 0.6/0.3 | gap set for 90 Ω |
| RF50 | `RF*`, `ANT*` | from calc | ≥3×W | 0.6/0.3 | plus via fence |
| HV | `HV*`, mains | ≥0.5 mm | per creepage | — | reinforced by custom rule |

KiCad 9+ allows a net to belong to multiple netclasses; write rule conditions with
`A.hasNetclass('X')` rather than `A.NetClass == 'X'` so multiple membership behaves.

## 7. Tuning Profiles and Time-Domain Setup (KiCad 10)

For any bus with a timing budget (DDR, RGMII, high-speed serial, camera/display parallel):

- Create a **tuning profile** in Board Setup with per-layer track propagation data (each signal
  layer and its reference plane, target impedance, and propagation delay), then assign it to the
  netclass. The PCB Calculator derives propagation velocity from the stackup εr and geometry.
- With **Enable time domain tuning** checked, the length tuner and DRC work in **picoseconds**
  instead of millimetres — which is what actually matters when a bus is routed partly as
  microstrip (fast) and partly as stripline (slow), or crosses layers.
- Set pad-to-die delay on the package pads where the vendor publishes it; it is a first-class
  field in pad properties and can dominate the budget on short nets.
- Length/skew constraints in `.kicad_dru` can then be written directly in time units.
- When timing is not specified in time, stay in length mode — a fabricated delay number is worse
  than an honest length match.

## 8. Board Outline and Origins

- Draw `Edge.Cuts` as a single closed loop, arcs where the enclosure has radii, no duplicate or
  overlapping segments (the most common "board outline invalid" fab query). Slots and internal
  cutouts are separate closed loops on `Edge.Cuts`.
- Set the **drill/place origin** to a defined corner (usually bottom-left of the outline) and
  keep it stable across revisions — the assembler's CPL coordinates depend on it.
- Grid origin on a round number; place mounting holes and connectors from the mechanical drawing
  first, with keep-outs for screw heads, standoffs, and mating connector bodies.
- Import the enclosure DXF/STEP where one exists rather than transcribing dimensions.
