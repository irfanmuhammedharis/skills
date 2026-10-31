# Firmware Security: Crypto, Keys, Secure Boot, and Threat Modeling

## Contents
1. Threat modeling (do this first)
2. Cryptographic primitives — what to use, what to avoid
3. Key storage and secure elements
4. Secure boot chain
5. OTA security
6. Debug and production lockdown
7. Common catastrophic mistakes

---

## 1. Threat Modeling (do this first)

- List assets: device identity/keys, user data, control authority (what can this device actuate?), fleet integrity, cloud credentials.
- List attackers: remote network attacker, local physical attacker (debug ports, flash extraction), supply-chain attacker (malicious update server, counterfeit parts), insider (factory credential leak).
- STRIDE the data flows: spoofing (auth), tampering (integrity), repudiation (logs), information disclosure (confidentiality), DoS (availability), elevation (authz).
- For each threat: countermeasure or documented acceptance. Output: a one-page threat model in the firmware spec — certification auditors and enterprise customers ask for it.
- Industrial/OT products: frame the work against **IEC 62443** (zones and conduits, security levels SL1–SL4, component requirements 62443-4-2, development process 62443-4-1) — industrial customers procure against it; map each countermeasure to its SL claims. Key 62443 consequences for firmware: no default credentials, role-based access, signed updates, audit logs, and network segmentation assumptions stated in the manual.

## 2. Cryptographic Primitives — What to Use, What to Avoid

- Use only vetted libraries: mbedTLS, libsodium (via Monocypher for tiny MCUs), TF-M/PSA Crypto on Cortex-M33, vendor crypto accelerators (ESP32, STM32U5, nRF with CryptoCell).
- Signing firmware: ECDSA-P-256 + SHA-256 (or Ed25519). Never RSA-1024, never homebrew MACs for image authentication.
- Transport: TLS 1.2+ with ECDHE ciphers; validate certificates (full chain + hostname + expiry); pin the CA, not a leaf cert (leaf rotates).
- Symmetric: AES-128-GCM/CCM. Never ECB. Never reuse nonces in GCM (catastrophic — use random 96-bit nonces or counters with reboot-safe persistence).
- Randomness: use the hardware TRNG; seeding software PRNG from time/ADC noise alone is a classic break. Verify TRNG is enabled and health-checked.
- Hash: SHA-256. Never MD5/SHA-1 for anything security-relevant.
- Password-derived keys: PBKDF2/scrypt with salt — never raw hash of password.
- Never implement crypto yourself. The correct amount of hand-rolled crypto in production firmware is zero.

## 3. Key Storage and Secure Elements

- Hierarchy (best→worst): secure element (ATECC608A/B, STSAFE, NXP SE05x — keys never leave the chip, crypto done inside) → MCU TrustZone/secure flash (STM32U5, nRF5340, ESP32 with flash encryption + eFuse keys) → obfuscated flash storage with readout protection (acceptable only for low-value assets).
- Per-device unique keys provisioned at manufacture — see iot-firmware.md §2. A shared fleet key converts one device teardown into total fleet compromise.
- ATECC608 integration notes: I2C, needs cryptoauthlib; provision in a controlled jig; lock the config zone AFTER provisioning (irreversible — test the flow on sacrificial units first).

## 4. Secure Boot Chain

- Chain of trust: ROM bootloader → verifies bootloader signature → bootloader verifies app → app runs. Each link verified with an immutable root key (eFuse/OTP).
- Enable on: ESP32 (Secure Boot V2 + flash encryption), STM32U5/H5 (SBSFU/TF-M), nRF (MCUboot + immutable bootloader, KMU key storage), RP2350 (signed boot). For parts without hardware root (F4, AVR), secure boot is software-only — document the limitation.
- Anti-rollback: monotonic security counter in eFuse/OTP; without it an attacker re-flashes an old firmware with known vulnerabilities.
- Debug the boot chain deliberately: unsigned image rejected (test it), tampered image rejected (flip a bit, test it), old-version image rejected (test it).

## 5. OTA Security

- Non-negotiables: signature verification before every boot + before install; TLS for transport; version monotonicity; rollback to last-known-good (availability is also security — a bricked fleet is a successful attack).
- Update server compromise is in scope: image signing keys live offline (HSM or air-gapped), NOT in CI secrets with broad access; transport TLS is not a substitute for image signatures.
- Broadcast updates: consider sequence counters vs. replay; a recorded valid update packet must not be replayable to downgrade.
- See microcontrollers.md §6 and platform files for mechanics.

## 6. Debug and Production Lockdown

- Production build: JTAG/SWD locked (RDP L1 STM32, APPROTECT nRF, eFuse ESP32, RP2350 debug disable); UART shell removed or behind per-device credential; no `printf` of keys/secrets at any log level.
- Provide an authorized service path: challenge-response unlock (J-Link/STM32 authenticated debug) or physical reflash by service — "locked forever" bricks returns analysis; "open" invites cloning. Choose deliberately, document it.
- RMA flow: how to extract black-box data from a locked device (see debugging-methodology.md §5) — solve this before locking the first production unit.

## 7. Common Catastrophic Mistakes

- Hardcoded credentials in firmware strings (extractable from a flash dump in minutes).
- TLS without certificate validation (`esp_wifi` demos and MQTT examples often skip it — never copy that pattern).
- Unsigned OTA ("we'll add it later" — later never comes before the incident).
- Shared fleet API keys, MQTT wildcard subscriptions allowing cross-device command injection.
- UART bootloader left enabled with erase/write commands in production.
- Predictable device IDs as the only authentication.
- Storing PII/secrets in crash dumps or logs shipped to the cloud.
- Side-channel awareness: for high-value targets, power analysis extracts keys from unprotected software AES — this is what secure elements and crypto accelerators with DPA resistance are for. Assess whether your threat model includes physical attack; if yes, software-only crypto on a plain MCU is insufficient.
