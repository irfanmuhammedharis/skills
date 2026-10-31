# Antenna and RF Design for Embedded Devices

## Contents
1. Antenna selection by radio
2. Matching networks
3. PCB layout rules
4. Link budget calculation
5. Coexistence and EMI
6. Regulatory basics
7. Validation and test

---

## 1. Antenna Selection by Radio

| Radio | Typical antennas | Notes |
|---|---|---|
| BLE / Wi-Fi / Zigbee (2.4 GHz) | PCB inverted-F / meander, chip antenna, external whip/U.FL | PCB antenna cheapest; chip antenna easiest but needs keep-out; external best performance |
| Sub-GHz (433/868/915 MHz) | Helical, whip, PCB loop | Quarter-wave whip at 868 MHz ≈ 82 mm — size often forces external |
| LoRa | Same as sub-GHz | Efficiency dominates range more than TX power |
| GNSS | Active ceramic patch, helix | Needs LNA supply (3.3/5 V bias-tee); ground plane size affects gain strongly |
| Cellular LTE-M/NB-IoT | Flex PCB, external monopole | Wide band (700–2200 MHz) — use vendor-certified antenna; carrier certification may mandate specific antennas |
| 60 GHz radar | Integrated AiP | Do not place metal within the radar FOV; radome material must be RF-transparent |

Selection order: check if the module has an integrated certified antenna (easiest regulatory path) → external connector (best performance, enclosure-dependent) → chip antenna → custom PCB antenna (needs VNA tuning; only with RF capability on the team).

## 2. Matching Networks

- Always place a π-network (series + two shunt pads) between radio and antenna, even if you populate it as 0 Ω + DNP. Untuned designs are unfixable without a board spin.
- Target: |S11| < −10 dB across the operating band (better than −6 dB absolute minimum), measured with a VNA on the final enclosure+PCB assembly.
- Matching changes with enclosure, battery, nearby metal, and hand/body proximity — measure in the final mechanical configuration.
- Keep the RF trace 50 Ω controlled impedance: compute width from stackup (state dielectric, height, Er); keep it short, no vias if possible, solid ground beneath.

## 3. PCB Layout Rules

- Follow the module vendor's reference layout exactly for the RF section — deviation voids modular certification assumptions.
- Ground plane: uninterrupted under the RF path and module; via stitching around the RF trace edges.
- Antenna keep-out: no copper (any layer) under/around PCB or chip antennas per datasheet; no metal (battery, shielding, displays) within the keep-out; plastic enclosure ≥ a few mm away.
- Crystals: short symmetric traces, guard ground ring, no signals crossing beneath.
- Decoupling at the radio: bulk cap sized for TX current pulses near the radio power pins; RF PA supply routed wide and short.
- Never route high-speed digital (SDIO, USB, display clocks, switching regulators) near the antenna; switching regulator harmonics at the radio band = desense. Use shielded inductors and spread-spectrum if available.

## 4. Link Budget Calculation

Show this math for every wireless design:

```
RX power (dBm) = TX power + TX antenna gain − path loss + RX antenna gain − margin
Path loss (free space, dB) = 20·log10(d_km) + 20·log10(f_MHz) + 32.44
```

- Compare RX power vs. receiver sensitivity (datasheet, at the actual data rate/SF); require ≥10 dB link margin for indoor/urban, ≥20 dB where reliability matters.
- Indoor: add 10–30 dB per wall depending on material; body loss near 2.4 GHz wearables: 10–20 dB.
- Example: BLE at 0 dBm TX, −95 dBm sensitivity, free-space budget 95 dB → ~1 km line-of-sight, but indoors assume 3–6 dB/10 m path exponent → realistic 10–30 m. State assumptions.

## 5. Coexistence and EMI

- Wi-Fi + BLE same chip: time-division on shared antenna — expect BLE throughput drops during Wi-Fi TX.
- GNSS + cellular: cellular TX harmonics desensitize GNSS — filter/isolate, and test GPS lock during data transmission.
- Radar (60 GHz) + 2.4 GHz: no direct interference, but radar MCU clock harmonics can leak — shielding review.
- Switching regulators: choose frequencies whose harmonics avoid the RX band; verify with near-field probe or at minimum conducted measurement.

## 6. Regulatory Basics (Design Consequences, Not Legal Advice)

- Pre-certified modules (ESP32-WROOM, nRF52 modules, etc.): keep the reference layout and antenna type — then only intentional-radiator requirements are largely inherited; change the antenna and you may need re-certification.
- ISM band rules differ: FCC 915 MHz (US, frequency hopping or DSSS, higher power OK), ETSI 868 MHz (EU, duty-cycle 0.1–10% per sub-band), 2.4 GHz worldwide but power/EIRP limits differ.
- Duty-cycle enforcement is firmware's responsibility on LoRa/sub-GHz in EU — implement airtime accounting.
- SAR evaluation may apply for body-worn >20 mW devices.
- Plan pre-compliance testing (radiated emissions + spurious) before formal certification; fixes are 10× cheaper pre-cert.

## 7. Validation and Test

- Minimum RF validation without a lab: RSSI sweep at known distances/orientations vs. a reference device; packet-error-rate test at margin boundary (≤1% PER target at deployment distance); test inside final enclosure.
- With a VNA: verify S11 across band in final assembly.
- With a spectrum analyzer: check TX power, harmonics, spurious vs. regulatory mask.
- Over-the-air firmware behavior: verify the radio stack degrades gracefully at the edge of range (retries, buffering, no watchdog resets from stack stalls).
