# PCB Layout for Embedded Products

Layout is where schematic intent meets physics. Most EMI, ADC noise, and RF failures are layout failures.

## Contents
1. Stackup and design rules
2. Placement strategy (before routing)
3. Grounding and return paths
4. Decoupling and power routing
5. Mixed-signal rules
6. High-speed and RF rules
7. High-current and thermal
8. Design review checklist and DFM

---

## 1. Stackup and Design Rules

- 2-layer: acceptable for simple low-speed boards — route ground as a grid, keep loops tiny, expect to work harder.
- 4-layer (SIG-GND-PWR-SIG) is the product default: unbroken ground plane under everything pays for itself in EMI and debug time.
- Set the fab's design rules into the CAD first (min trace/space, via drill, annular ring) — designing to rules you can't manufacture is scrap.
- Controlled impedance only matters for RF (see antenna-rf.md) and fast buses (USB 90 Ω diff) — get the fab stackup, compute widths, document.

## 2. Placement Strategy (Before Routing)

- Place by function block, following the schematic sheets: power → MCU → crystal → radio → sensors → connectors. Connectors are fixed by enclosure/mechanics first.
- Crystal: adjacent to MCU, shortest possible symmetric traces, guard ground, nothing under it.
- Decoupling caps: at the pins they serve — a 100 nF 5 mm away is decoration.
- Buck converter: input cap → IC → inductor → output cap as one tight cluster; hot loop (switch node) area minimized.
- Sensors: away from heat sources (regulators, MCU at full tilt, battery charger) — a temperature sensor 5 mm from an LDO reads the LDO. IMU away from connectors/board flex points (stress = offset).
- Antenna zone per vendor layout — sacred ground (antenna-rf.md §3).
- Test points and programming pads accessible for the production fixture (hardware-review.md §3).

## 3. Grounding and Return Paths

- Every signal has a return current directly beneath it on the ground plane — never route a signal over a plane split; the return detour is the EMI antenna.
- Star/split grounds: for mixed-signal, keep analog and digital return regions separate by placement (not by cutting the plane — splits cause more problems than they solve in 90% of designs); join at one point near the ADC/reference.
- Via stitching: ground vias at layer transitions of signals (return path follows), around the board edge (~λ/20 or few-mm grid) forming a Faraday cage edge, dense stitching around RF sections.
- Connectors: chassis/ESD ground separate from signal ground, joined via cap + R, TVS returns to chassis ground — ESD current must not traverse the logic ground.

## 4. Decoupling and Power Routing

- Per-pin 100 nF X7R within 2 mm, short via to plane; bulk 10–100 µF per power entry; radio modules get their own bulk per vendor app note.
- Power traces sized for current: 1 oz copper ≈ 0.5 mm/20 mil per amp (external layers, modest rise) — use a calculator, state the assumption; use planes or polygons for anything >500 mA.
- Keep switching regulator loops away from analog/RF: separate the buck's hot loop physically; inductor is a field emitter — shielded type, not under the antenna.
- Sense lines (feedback, current sense) routed quiet: away from switch nodes, kelvin-connected at the shunt.

## 5. Mixed-Signal Rules

- ADC inputs: short, over ground, no parallel run with digital clocks; RC filter at the ADC pin; reference decoupled per datasheet (often specific cap+ferrite).
- Clocks (crystal, MCU clock out, SPI/SDIO): short, over solid ground, via-stitched guard for aggressors near analog.
- USB/SDIO/high-speed: length-match where the spec demands (USB D+/D− skew, SDIO modest), controlled impedance where spec'd, no stubs.
- Level shifters placed at the domain boundary they serve.

## 6. High-Speed and RF Rules

- RF section replicates the module reference layout exactly — copy the keep-outs, feed line width, via fences (antenna-rf.md §2–3).
- Series R placeholders (22–47 Ω) on fast digital outputs (SPI, clocks) near the driver — rise-time control when EMI shows up.
- No routing under the antenna keep-out on ANY layer; battery/metal/display clearance respected.
- ESD: TVS within mm of the connector, short fat ground return; ESD current path never crosses the board.

## 7. High-Current and Thermal

- Motor/relay/heater currents: wide polygons, heavy copper option (2 oz), connector current rating with 2× margin per pin (parallel pins for more).
- Thermal: copper pours as heatsinks with via arrays under thermal pads (θJA math from circuit-design.md §2); hot parts away from temperature sensors and electrolytics (their lifetime halves per 10 °C).
- Creepage/clearance for mains voltages: slots under optos/relays, spacing per the voltage class — this is a safety item, not a preference.

## 8. Design Review Checklist and DFM

Run before fab, with evidence:
- [ ] Every net from schematic accounted for (no "R6 pin 1 NC by accident")
- [ ] All decoupling at pins; all bulk caps placed per §4
- [ ] No signal crosses a plane split; return vias at layer changes
- [ ] Crystal/switch-node/antenna zones clean per §2/§6
- [ ] Power trace widths verified vs. current (math in notes)
- [ ] Test points on all rails + key signals; programming pads on grid for pogo fixture
- [ ] Silkscreen: pin-1 marks, polarity marks, connector labels, board rev
- [ ] Fiducials (3) if machine-assembled; panelization/tooling holes per assembler
- [ ] DRC clean with the fab's rule set; 3D fit check against enclosure CAD
- [ ] Thermal: thermal-pad via arrays present; hot parts placed per §7
- [ ] DFM export: gerbers + drill + pick-and-place + centroid verified (view them yourself — don't trust the export)
