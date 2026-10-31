# Electrical Correctness Checklist

Run this **before drawing** every diagram. Each item below is a real, common mistake
that silently breaks a build. If a rule depends on hardware you don't know (e.g.,
buzzer type), ask — or design the diagram to work for **both** variants.

## Power & Ground
- [ ] **Never** a direct 5V → GND path (short circuit). Every 5V wire must pass through
      a component (resistor, LED, sensor, motor, etc.).
- [ ] 5V and GND travel on the red `+` / blue `−` rails, not through random holes.
- [ ] Sensors/boards that need clean power (HC-05, servo, motors) are clearly marked;
      motors run from a **separate battery** through the driver, never from the 5V rail.

## LEDs
- [ ] Every LED has a **current-limiting resistor** (220Ω–330Ω for 5V).
- [ ] Polarity correct: **long leg (anode) → resistor → signal pin**; short leg
      (cathode) → GND. (Some LEDs/boards have a flat edge marking the cathode.)
- [ ] LED drawing shows anode/cathode clearly; label which leg is which if ambiguous.

## Buttons & Switches
- [ ] With `INPUT_PULLUP` in code, button connects **pin ↔ GND** (pressed = LOW).
- [ ] Without pull-up, button connects pin ↔ 5V with a 10kΩ pulldown to GND.
- [ ] Draw which two legs of the button are used (opposite sides).

## Servo
- [ ] Signal wire → a **PWM-capable pin** (Servo library works on any pin, but PWM
      pins are the safe choice: D3, D5, D6, D9, D10, D11 on Uno).
- [ ] Red → 5V (or external 5V for stronger servos), brown/black → GND.
- [ ] Never connect the servo to the Arduino's 5V rail if the datasheet says external
      supply — note it on the diagram.

## Sensors
- [ ] **HC-SR04**: VCC → 5V, GND → GND, Trig → a digital OUT pin, Echo → a digital IN
      pin (Echo is 5V — fine on Uno; on 3.3V boards use a divider).
- [ ] **DHT11 bare (3-pin)**: needs a **4.7kΩ–10kΩ pull-up** from DATA to 5V.
      The blue 4-pin module already has it — draw the pull-up only for the bare sensor.
- [ ] **MQ3 / MQ-x**: heater pin to 5V, AO → analog pin, needs warm-up (state it).
- [ ] **PIR**: VCC → 5V, OUT → digital pin, GND → GND; note 2–60 s warm-up.
- [ ] **Sound sensor (KY-037)**: VCC/GND/DO; polarity of DO varies by module — note
      that the code may need `HIGH` ↔ `LOW` flipped (see "If in doubt" below).
- [ ] **IR line sensors**: VCC/GND/OUT; OUT logic for black-vs-white varies — the
      diagram must match the code comment, and the code should say which is which.

## I2C (LCD, RTC, etc.)
- [ ] SDA → A4, SCL → A5 on Uno (or dedicated I2C pins on other boards).
- [ ] VCC → 5V (3.3V I2C boards exist — check), GND → GND.
- [ ] Address noted (`0x27` or `0x3F` for the common LCD; code must match).

## Buzzer
- [ ] **Drive with `tone()` / `noTone()`**, which works with BOTH active and passive
      buzzers. Driving a passive buzzer with `digitalWrite(HIGH)` produces no sound.
- [ ] If `digitalWrite` is used, the diagram must note "active buzzer only".

## Relay
- [ ] VCC → 5V, GND → GND, IN → digital pin.
- [ ] Relay modules vary: **active-HIGH** (ON with HIGH) vs **active-LOW** (ON with
      LOW). Diagram + code must be consistent, and a "if it works backwards, swap
      HIGH/LOW" note is good practice.
- [ ] Load (lamp/motor) on COM/NO — mark COM/NO clearly; mains power only by adults.

## Motor Driver (L293D / module)
- [ ] IN1–IN4 → 4 digital pins; EN pins → 5V (or PWM pins if speed control).
- [ ] VCC1 (logic) → 5V; VCC2/VM → **battery +**; GND → common ground (battery − AND
      Arduino GND).
- [ ] Motors A/B wired to OUT1–4; a swapped motor plug makes the robot drive backwards —
      the diagram should label which plug is left vs right.

## Serial / Bluetooth
- [ ] **HC-05 TX → Arduino RX, HC-05 RX → Arduino TX** (cross-over!). With
      `SoftwareSerial(rxPin, txPin)`, HC-05 TX → rxPin, HC-05 RX → txPin.
- [ ] HC-05 RX is **3.3 V logic** — note "unplug RX during upload" or draw a divider.
- [ ] Baud rate (9600 default) matches the code.

## Diagram Hygiene (caught by verify_diagram.py)
- [ ] Every wire endpoint on a pin/hole/rail — nothing dangles.
- [ ] Every component labeled; labels inside the viewBox.
- [ ] Wiring JSON lists every drawn wire (from/to/color/note).
- [ ] Pin numbers in the code match the spec (the checker compares them).

## If in doubt
Never guess a polarity, pull-up, address, or pin. Either:
1. ask the user for the exact part/module, or
2. design to work for both variants and add a short "if it acts backwards, swap X"
   note — the diagram then stays correct no matter which module they own.
