# Routing, Vias, and Copper Pours

## Contents
1. Routing order and the router
2. Track geometry
3. Vias and layer transitions
4. Ground and power planes
5. Zone settings that matter
6. Teardrops, fills, and finishing
7. Common routing failures

---

## 1. Routing Order and the Router

Route in decreasing order of consequence:

1. Nets with a physical constraint: RF, crystal, differential pairs, anything impedance
   controlled or length matched.
2. Power delivery: input path, converter loops, rails to loads (polygons, not tracks, above
   ~500 mA).
3. Sensitive analog and reference nets.
4. Fast digital buses, then everything else.
5. Ground last only in the sense that it is *poured* last — the ground *plan* exists from the
   start.

Use KiCad's interactive router in **Highlight collisions** or **Shove** mode with "Allow DRC
violations" off; the router respects netclass widths and custom rules, so correct setup means
the router enforces the design for you. Differential pair router for pairs; tuning tools for
length/delay. Autorouters (including the freerouting bridge) are acceptable only for
low-consequence nets on simple boards, and the result must be reviewed track by track.

## 2. Track Geometry

- Width from the netclass, which came from a calculation. Widen power tracks toward the source;
  never neck a power net through a default-width segment.
- Angles: 45° or arcs. Acute angles create acid traps and impedance discontinuities; KiCad's
  router produces clean 45° geometry by default — keep it.
- Keep tracks off the board edge by at least the fab's copper-to-edge value (0.3 mm is a safe
  default).
- Don't route through a component's courtyard on the same layer if the part could be reworked;
  avoid tracks under crystals, inductors, and antennas entirely.
- Match the fan-out style to the part: BGAs get dog-bone escapes with a via per ball and a
  neck-down rule inside the courtyard; QFNs get short traces out of the pad before via placement.
- Series termination resistors and pull-ups go at the driver (series) or the receiver (parallel/
  pull-ups) — placement matters more than the value.

## 3. Vias and Layer Transitions

- Standard via 0.6 mm pad / 0.3 mm drill unless a calculation says otherwise; the fab's cheapest
  via is usually 0.45/0.3.
- **Every layer change on a signal that matters needs a return path**: a ground via within a few
  mm (ideally <2 mm) for a signal moving between layers referenced to different planes; if both
  layers reference the *same* plane, the return is continuous and no stitching via is required.
- Current-carrying vias: size and count from `pcb_calc.py via-current`. One via per amp is a
  reasonable rule of thumb for 0.3 mm plated vias, but compute it and add margin.
- Via stitching: around board edges (grid of a few mm) to form a Faraday cage, along the RF
  ground pour, and beside every high-speed layer transition.
- Via-in-pad only with filled/capped vias declared in the fab notes. Uncapped via-in-pad wicks
  solder and creates voids.
- Microvias/blind/buried only when the fab supports them and the density demands them; they
  multiply cost. Disallow them by rule if not intended.
- Tenting: tent vias by default (mask over) except test/probe vias; specify tenting in the fab
  notes and check the mask gerbers show what you expect.

## 4. Ground and Power Planes

- A ground plane is a return path, not a copper decoration. Its value is being **unbroken** under
  the signals that use it.
- Never route signals across a plane on a layer that acts as the reference for other signals if
  the track will slice it; on a 4-layer `SIG/GND/PWR/SIG` board, keep L2 as pure ground.
- Power planes: split by rail with generous gaps, and check that no fast signal crosses a split.
  On 4-layer boards, routing power as wide tracks/polygons and keeping both inner layers as
  ground is often better for EMI.
- Stitch top and bottom ground pours to the plane liberally; unstitched pour islands are
  antennas, and KiCad will report isolated copper islands — fix them rather than hiding them.
- Analog and digital ground: separate by *placement and pour geometry*, joined at a single point
  near the converter, only when a datasheet or a real measurement demands it. Cutting planes is
  a more common cause of EMI than a cure for it.
- Chassis/shield ground: its own region, connected to signal ground through the intended
  component (cap, resistor, or direct at one point), with ESD current routed there deliberately.

## 5. Zone Settings That Matter

- **Clearance**: usually the netclass clearance; larger for HV zones.
- **Minimum width**: keep above the fab minimum so slivers do not appear (0.25 mm is a
  reasonable floor).
- **Thermal relief vs solid**: thermal reliefs for hand-solderable THT pads (otherwise the joint
  wicks heat and never wets); solid for power pads, heatsink pads, and anything carrying current.
  Set per-pad or by rule (`zone_connection`, `thermal_spoke_width`, `min_resolved_spokes`).
- **Fill type**: solid for real copper; hatched only where flex or plating balance requires it.
- **Island removal**: remove islands, or set a minimum island area — dead copper is a floating
  antenna.
- **Priority**: overlapping zones need explicit priorities (e.g. a small analog ground island
  inside a larger digital pour).
- Refill zones before every DRC and every export; a stale fill hides violations.
  `kicad-cli pcb drc --refill-zones --save-board …` makes this deterministic in CI.

## 6. Teardrops, Fills, and Finishing

- Teardrops on pads and vias improve mechanical reliability and drill-registration margin;
  KiCad generates them natively per-netclass or globally. Enable them, then re-run DRC — they
  can shrink clearances.
- Length tuning last, after the routing topology is final (meanders are the first thing you lose
  in a re-route).
- Silkscreen pass at the end: reference designators readable, ≥1 mm text, not over pads or vias
  (`silk_clearance` rule), pin-1 and polarity marks intact, connector functions labelled, board
  name/rev/date present.
- Copper balance: add non-functional pour or a hatched area to even out copper distribution if
  one region is bare — it reduces warp and etch variation.

## 7. Common Routing Failures

| Symptom found later | Cause in routing |
|---|---|
| Radiated emissions fail EMC | Signal crossed a plane split; hot loop too large; no return via at layer change |
| ADC noisy at LSBs | Analog input routed beside a clock or over a switching node |
| USB enumeration marginal | Pair not routed as a pair, uncoupled at fanout, impedance wrong, stub at a test point |
| Board works cold, fails hot | Power trace sized for typical current; no thermal relief on the plane; via count too low |
| Assembly shorts | Silkscreen over pads, teardrops added after DRC, pour min width below fab capability |
| Field failures at the connector | ESD path routed across the board rather than to chassis ground at the connector |
