# Sensors: Selection, Interfacing, Calibration, and Failure Modes

## Contents
1. Sensor selection by measurand
2. Interface design rules
3. Signal conditioning and filtering
4. Calibration and compensation
5. Failure modes and diagnostics
6. Common part-specific notes

---

## 1. Sensor Selection by Measurand

| Measurand | Common parts | Interface | Key spec to check |
|---|---|---|---|
| Temperature | DS18B20, TMP117, NTC thermistor, PT100/1000 | 1-Wire, I2C, analog | Accuracy across range, self-heating |
| Humidity | SHT31/45, HDC2080 | I2C | Condensation behavior, long-term drift |
| Pressure | BMP390, LPS22, MS5611 | I2C/SPI | Absolute vs. relative, noise floor |
| IMU/accel/gyro | MPU6050, LSM6DS3, BMI270, ICM-42688 | I2C/SPI | Noise density, offset drift, ODR |
| Magnetometer | LIS3MDL, BMM150 | I2C/SPI | Hard/soft-iron interference on PCB |
| ToF distance | VL53L0X/L1X/L4 | I2C | Range vs. target reflectivity, crosstalk |
| Ultrasonic | HC-SR04, waterproof JSN-SR04T | GPIO/PWM | Blind zone, beam angle |
| mmWave radar | Seeed MR60BHA2, IWR6843 | UART | Presence vs. fall-detection variant, mounting height constraints |
| Gas | MQ series, SGP30/40, SCD41 (CO2) | Analog/I2C | Burn-in time, cross-sensitivity, calibration gas |
| Current/voltage | INA219/226, ACS712, HLW8012 | I2C/analog | Isolation, shunt sizing |
| Optical/pulse | MAX30102 (PPG), TSL2591 | I2C | Ambient rejection, LED drive current |
| Biosignal | ADS1292 (ECG), MLX90614 (IR temp) | SPI/I2C | Medical-grade front-end requirements |
| Load cells | HX711 + strain gauge | Digital | Noise vs. sample rate, excitation stability |
| GNSS | u-blox NEO-M9/M10, Quectel L96 | UART | TTFF, antenna supply, PPS timing |

## 2. Interface Design Rules

- **I2C sensors**: verify pull-up sizing (show calculation: Rp min from sink current, Rp max from rise time with bus capacitance); scan the bus at boot and fail loudly if an expected address is absent; many cheap sensors hang the bus on power glitch — implement bus-recovery (9 clock pulses on SCL).
- **SPI sensors**: respect max clock, mode (CPOL/CPHA), and CS setup/hold; shared-bus sensors must tri-state MISO properly — verify or add series resistors.
- **Analog sensors**: buffer high-impedance sources; account for ADC input leakage; ratiometric sensors (strain gauge, some pressure) must share the ADC reference with the excitation.
- **UART sensors**: validate every frame (header, length, checksum); handle partial frames and garbage after power glitch; radar/CO2 sensors often stream continuously — drain the buffer or it overflows silently.

## 3. Signal Conditioning and Filtering

- Choose filter by noise spectrum, not habit: moving average for white noise reduction, median filter for spike rejection (glitches, ESD), exponential/IIR for smooth control signals, Kalman/complementary for IMU fusion.
- State filter parameters with sampling rate — a cutoff frequency without Fs is meaningless.
- Oversampling + decimation: each 4× oversample adds ~1 bit effective resolution; show the tradeoff in output data rate.
- Plausibility layer before the filter: reject readings outside physical range (e.g., temperature step >10 °C/s) before they contaminate the filter state.

## 4. Calibration and Compensation

- Every production device needs at minimum a single-point offset calibration stored in flash with CRC and a factory-default fallback.
- Two-point (offset + gain) for analog chains; temperature compensation table for pressure/gas/IMU where the datasheet gives drift coefficients.
- Never calibrate over the factory values — write to a separate calibration sector with versioning.
- Document the calibration procedure in the production runbook: stimulus, wait time, pass criteria, data stored.

## 5. Failure Modes and Diagnostics

Design for these explicitly — each needs a detection method and a defined system response:

- **Stuck value** (sensor returns identical reads): track a stale counter; reset power or re-init after N stale samples.
- **Bus lockup**: I2C recovery sequence; power-cycle sensor rail if available.
- **Out-of-range**: sensor disconnected (0 V, full-scale, NaN) vs. genuine extreme — distinguish open-circuit from valid reading (check pull behavior).
- **Slow drift**: baseline tracking for gas/PPG sensors; flag when recalibration is needed.
- **Power sequencing**: many sensors need defined power-up delay before first communication (check tBOOT in datasheet); first reads after wake are often garbage — discard per datasheet.
- **Self-test**: use built-in self-test bits (IMUs, pressure sensors) at boot where available.

## 6. Common Part-Specific Notes

- **DS18B20**: parasitic power is unreliable — use external VDD; conversion takes 750 ms at 12-bit — do not block.
- **HX711**: 80 SPS mode needs different clock count; power-down via PD_SCK high >60 µs.
- **MAX30102**: needs ambient-light subtraction and motion artifact rejection for any pulse reading; raw PPG without filtering is unusable.
- **MR60BHA2 (60 GHz radar)**: UART 115200, reports heart/breath rate only with stationary target within ~1.5 m; mounting orientation matters; validate against a reference device — do not treat output as medical-grade.
- **MQ gas sensors**: heater draws ~150 mA; require 24–48 h burn-in; readings are relative (Rs/R0) — cannot produce absolute ppm without calibration gas.
- **HC-SR04**: 5 V logic — level-shift the echo pin down to 3.3 V; echo timeout must be implemented (no object = no echo = infinite wait otherwise).
- **BME280/BMP390**: forced mode for battery devices; IIR filter coefficient changes effective response time — state it.
