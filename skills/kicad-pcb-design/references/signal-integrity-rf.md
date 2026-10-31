# Signal Integrity, High Speed, and RF

## Contents
1. When a signal is "fast"
2. Controlled impedance in practice
3. Differential pairs
4. Length matching and time-domain tuning
5. Return paths and layer transitions
6. Per-interface recipes
7. RF sections
8. EMC by construction

---

## 1. When a Signal Is "Fast"

Frequency is not the criterion — **edge rate** is. A signal needs transmission-line treatment
when the propagation delay along the track exceeds roughly one third of the signal's rise time.

On FR-4, propagation is ≈ 6.7 ps/mm for microstrip (εr 4.4) and ≈ 7.1 ps/mm for stripline (use
`pcb_calc.py prop-delay`). A 1 ns rise time therefore starts caring at roughly 50 mm; a 200 ps
edge (common on modern CMOS outputs even at low clock rates) cares at ~10 mm. This is why a
16 MHz SPI bus can radiate: it is the edge, not the clock.

Consequences: series termination (22–47 Ω at the driver) on fast digital outputs is cheap
insurance; keep the option in the schematic even if you fit 0 Ω.

## 2. Controlled Impedance in Practice

- Impedance depends on trace width, dielectric height to the **nearest reference plane**, copper
  thickness, εr, and solder mask. Only the fab's stackup numbers give a real answer.
- Workflow: choose a fab stackup → get εr and dielectric thickness → solve for width
  (`pcb_calc.py microstrip --z0 50 --er 4.4 --h 0.2104 --t 0.035`) → cross-check with the fab's
  impedance calculator → set the width in the netclass → write a `track_width` rule so nothing
  drifts → mark the board as impedance-controlled in the fab notes.
- Tolerance is typically ±10%; for tighter, the fab must test-coupon the panel (extra cost).
- Common targets: 50 Ω single-ended (RF, general), 90 Ω differential (USB 2.0), 100 Ω
  differential (Ethernet, LVDS, HDMI pairs, MIPI), 85 Ω (PCIe, some USB 3), 75 Ω (video).
- A microstrip's reference is the plane directly beneath. Change layers and you change impedance
  unless the new layer has an equivalent reference at an equivalent distance.

## 3. Differential Pairs

- Name nets `<BASE>_P` / `<BASE>_N` so KiCad recognises the pair for routing, tuning, and
  `inDiffPair()` rules.
- Differential impedance is set by width **and** gap; a tighter gap lowers Zdiff. Solve both
  together (`pcb_calc.py diff-microstrip`), don't tweak one.
- Route the pair together, symmetrically, on one layer where possible. Keep the uncoupled length
  (fanout, via transitions) minimal — enforce with `diff_pair_uncoupled`.
- Intra-pair skew: match the two halves tightly (USB 2.0: within ~0.15 mm; faster standards
  tighter or specified in ps). Correct skew at the source of the mismatch, not at the far end.
- Keep other signals at least 3× the pair gap away (5× for aggressive aggressors); ground pours
  beside pairs need stitching or they couple.
- Avoid vias in pairs; when unavoidable, place them symmetrically with adjacent ground vias.

## 4. Length Matching and Time-Domain Tuning

- Match against a **budget**, not a habit: derive the allowed skew from the interface spec
  (setup/hold, or the standard's stated tolerance), then tune to it.
- Length mode is fine when everything is on one layer type. Use KiCad 10's **time-domain**
  tuning (tuning profile + `Enable time domain tuning`) when the group crosses layers,
  mixes microstrip and stripline, or when the spec is written in picoseconds. Add pad-to-die
  delay where the vendor publishes it.
- Meanders: amplitude ≥3× track width, keep serpentines away from the pair partner and from
  other nets, and don't tune inside a connector fanout.
- Enforce with `length` / `skew` constraints in `.kicad_dru` so a later re-route cannot silently
  break the match.

## 5. Return Paths and Layer Transitions

- Return current flows directly under the signal at high frequency. Anything that interrupts it —
  a plane split, a void, a big anti-pad field, a keepout — forces a detour, and the detour is the
  radiating loop.
- Layer change referenced to the *same* plane: return is continuous, no extra via needed.
  Layer change to a *different* reference plane: add a stitching via between the two planes
  (ground-to-ground) within a few mm; if the two references are ground and power, a stitching
  capacitor (100 nF, placed at the transition) is the equivalent.
- Connector and cable transitions are where boards radiate: ground the shield at the connector,
  keep the pair's reference continuous right up to the pads, no plane pull-back gap under the
  connector footprint.

## 6. Per-Interface Recipes

| Interface | Impedance | Key rules |
|---|---|---|
| USB 2.0 HS | 90 Ω diff | Pair on one layer, ≤ ~0.15 mm intra-pair skew, no stubs, ESD diodes at connector with low capacitance (<1 pF), keep pair away from switchers |
| USB-C (CC/SBU) | — | CC resistors correct for role; VBUS protection sized for 5 V/3 A minimum |
| Ethernet 10/100/1000 | 100 Ω diff | Magnetics placed at the connector; chassis-ground island under the RJ45 with a stitched capacitor; no copper under the isolation gap |
| SPI/QSPI | — | Series R at driver; keep clock away from analog; length match only when the clock period demands it |
| I²C | — | Pull-ups sized for bus capacitance and speed (typ. 2.2–4.7 kΩ at 400 kHz); keep total capacitance < 400 pF |
| SDIO/eMMC | 50 Ω SE | Length match the group, series R on CLK, solid reference throughout |
| DDR | 40/80 Ω typ. | Byte-lane matched in time domain; fly-by topology per vendor; VREF decoupled locally; this is where tuning profiles earn their keep |
| Camera/Display MIPI | 100 Ω diff | Tight pair matching, minimal vias, reference continuity absolute |
| RF (Wi-Fi/BLE/LoRa/GNSS) | 50 Ω | See §7 |

## 7. RF Sections

- Copy the module or chip vendor's reference layout **exactly**: feed line geometry, matching
  network placement, ground via fence spacing, and the antenna keep-out shape.
- Antenna keep-out: no copper on **any** layer, no components, no battery or metal within the
  vendor's stated clearance; board edge placement as specified; the keep-out enforced with a
  named rule area + `disallow` rule.
- Feed line: coplanar waveguide with ground (CPWG) or microstrip at exactly 50 Ω, as short and
  straight as possible, via-fenced on both sides at ≤ λ/20 spacing.
- Matching network: π-network footprints (three positions) even if you only fit one part —
  tuning after measurement is normal, and unpopulated pads cost nothing.
- Keep switching converters, high-current loops, and crystals physically distant; put the radio's
  own decoupling and bulk exactly per the app note.
- Plan for measurement: a u.FL/SMA footprint (DNP in production) pays for itself the first time
  the antenna underperforms.

## 8. EMC by Construction

- Small loops everywhere (see placement.md §2) — this is 80% of EMC.
- Filter at the boundary: every wire leaving the enclosure gets a filter/TVS at the connector,
  referenced to chassis ground.
- Controlled edge rates: use the slowest drive strength the design tolerates; series resistors on
  clocks and fast outputs.
- Common-mode chokes on differential cable interfaces (USB, Ethernet, CAN) placed at the
  connector.
- Guard/stitching: board-edge via fence, stitched pours, no long unstitched slivers.
- Shielding is a fix for a design that already got the above right — it is not a substitute, and
  a shield with a poor ground contact makes emissions worse.
