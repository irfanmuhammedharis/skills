# Placement

Placement determines whether routing is pleasant or impossible, and it decides EMI and thermal
performance before a single track exists. Budget real time here; expect to redo it once.

## Contents
1. Order of operations
2. Loop-area thinking
3. Block-by-block placement rules
4. Mechanical and assembly constraints
5. When placement is finished

---

## 1. Order of Operations

1. **Board outline, mounting holes, keep-outs** from the mechanical drawing.
2. **Mechanically fixed parts**: connectors, switches, LEDs, displays, antennas, sensors that
   must see the outside world. These cannot move later; everything else serves them.
3. **Power path**: input protection → converters → bulk capacitance, placed near where the power
   enters and near the loads they feed.
4. **Big ICs**: MCU/SoC oriented so its buses face the parts they talk to; rotate the part to
   minimise crossings — rotation is free now and expensive after routing.
5. **The tight clusters**: converter hot loops, crystal, radio matching network, ADC front end.
6. **Decoupling**: at the pins, placed before the general small parts.
7. **Everything else**, then test points, fiducials, and silkscreen.

Use the ratsnest as a placement metric: rotate and swap until the rat's nest is visually
untangled. Ratsnest crossings that survive placement become vias.

## 2. Loop-Area Thinking

Every current has a return. Placement is really the art of making the loops small:

- Switching converter **hot loop** (input cap → high-side switch → low-side switch/diode → back
  to cap): the smallest loop on the board, all on the top layer, with an unbroken ground plane
  directly under it. This single loop dominates a board's radiated emissions.
- Decoupling loop: IC pin → cap → via → plane → via → IC ground pin. Place the cap so its via is
  on the far side from the pin, and keep the via right at the pad — a 100 nF cap 5 mm away with a
  long trace is decoration.
- Crystal loop: crystal + both load caps + MCU pins, tiny, with a local ground under them.
- Load loops: high-current loads (motors, relays, LED strings) get their return path planned,
  not inherited.

## 3. Block-by-Block Placement Rules

- **Regulators/converters**: inductor away from analog and antenna; feedback node small and away
  from the switch node; output caps between the inductor and the load; thermal copper planned
  (power-thermal.md). Keep the switching node copper area minimal — it is the aggressor.
- **Crystal/oscillator**: adjacent to the MCU, symmetric short traces, ground guard ring, no
  routing or copper pour of other nets underneath on any layer.
- **Radio module / antenna**: replicate the vendor's reference layout exactly — keep-out zone,
  feed line width, ground via fence, and board-edge placement. No copper on any layer under the
  antenna keep-out, no battery or metal within the vendor's stated clearance.
- **Analog / ADC**: away from converters, digital clocks, and hot parts; reference and input
  filters at the pin; the return current path kept out of digital return regions by placement,
  not by cutting the plane.
- **Sensors**: temperature sensors away from any heat source (a sensor 5 mm from an LDO reads the
  LDO); IMUs away from board flex and connector stress; optical parts on the mechanical
  centreline they need.
- **Connectors**: at the enclosure openings, with ESD parts placed *at* the connector, mating
  clearance respected, and the insertion force path over mounting holes, not over fine-pitch ICs.
- **High voltage**: physically separated region with the isolation barrier drawn on the board and
  no traces, planes, or components crossing it except through the isolator.

## 4. Mechanical and Assembly Constraints

- Check the enclosure in 3D early: export STEP after placement, not after routing.
- Component heights: tall parts (electrolytics, connectors, relays) checked against enclosure
  clearance and against each other for tool access.
- Keep-outs for screw heads, standoffs, and any moving part.
- Assembly-friendly: consistent orientation for polarised parts (all diodes/caps facing the same
  way per region) makes visual inspection fast and misplacement obvious.
- Courtyards must not overlap — enable that check as an error, not a warning.
- Wave/selective solder or hand assembly on the bottom side: keep bottom-side SMD to a minimum,
  and respect the shadowing rules for THT parts.
- Panel edges: keep components ≥3–5 mm from the panel rail edge if the board will be routed out
  of a panel (see manufacturing-outputs.md).
- Test points reachable by a bed-of-nails fixture: on one side if possible, ≥1.27 mm pitch,
  ≥2.5 mm from tall components, not under a connector.

## 5. When Placement Is Finished

- [ ] Every mechanically constrained part matches the mechanical drawing (dimensions checked)
- [ ] 3D view shows no collisions with the enclosure or between parts
- [ ] Ratsnest is visibly untangled; the layer plan can carry what remains
- [ ] Every decoupling capacitor sits at the pin it serves
- [ ] Hot loops, crystal and RF clusters are tight and isolated
- [ ] Thermal sources are spread out and away from sensors and electrolytics
- [ ] Courtyard DRC clean, edge clearance respected
- [ ] Test points, fiducials, and mounting hardware placed
- [ ] Placement committed to version control before routing starts
