# Prototype tier

For a first spin, a dev/eval board, a jig, or a hobby build. The aim is a working board
fast and cheap, while dodging the handful of mistakes that make you order it twice.

## Defaults (state them, change on request)
- JLCPCB standard: 2 layers, 1.6 mm FR-4, 1 oz, HASL lead-free (ENIG if fine pitch ≤ 0.5 mm
  or there are edge contacts), green mask. `K apply_fab_preset("jlcpcb_2l_default")`.
- Design rules 0.2 mm track / 0.2 mm clearance unless density needs less. Vias 0.6/0.3 mm.
- Parts: JLCPCB **Basic** where possible (no setup fee), 0603 passives (0402 only if
  space-bound), common LDO/buck parts with good stock.
- Go to 4 layers if: USB HS or faster, Ethernet, RF module plus switching regulator in a small
  board, or more than ~2 BGA/QFN ICs. 4-layer at JLC is cheap now, so mention it.

## Still non-negotiable (each is cheap; skipping any is a classic respin)
- ERC/DRC gates, run for real.
- Footprint ↔ datasheet land pattern and pin-1 check for every IC and connector.
- Decoupling per datasheet at each power pin, plus bulk on each rail.
- GND pour (both sides on 2L) with stitching.
- Reverse-polarity protection and a fuse/PTC on any external power input. ESD diode on USB
  data and other user-touchable connectors.
- Programming/debug access (SWD/JTAG/UART/boot pins) reachable without bodges.
- Test pads on each rail and GND, and a power LED.
- Mounting holes (M3 by default) and a silk label with name + rev + date.
- Spare: 0 Ω jumpers/DNP pads on options you're unsure of (pull-ups, termination, boot straps).
  On a prototype, cheap optionality is worth the board space.

## Allowed shortcuts
- Autoroute non-critical nets after hand-routing power, clocks, USB/diff pairs and RF.
- Skip second sources, lifecycle research and IPC-2581. Gerber + drill + BOM + CPL is enough.
- Closed-form calculator results are fine without fab-calculator sign-off, if you say so.
- A shorter review: SKILL.md gate table plus the list above.

## Prototype → production handoff
When the user says "now make it production-ready", don't just re-export. Walk
`industrial-tier.md`, which usually means 4 layers, protection, DFT, second sources,
and fiducials. Treat it as a new revision.
