---
name: pi-zero-2w
description: "Build and run Rust, Python and C on a Raspberry Pi Zero 2 W (and Zero W v1). Use when targeting a Pi Zero, cross-compiling for ARM, choosing armhf vs arm64, fitting a program into 512 MB, picking an OS (Ubuntu vs Raspberry Pi OS), setting up headless Wi-Fi/SSH, tuning zram/swap, writing systemd units for a Pi, or debugging OOM kills, SD-card wear, or slow builds on a Pi."
---

# Raspberry Pi Zero 2 W — Rust, Python and C

The Zero 2 W is a 512 MB board with four Cortex-A53 cores. Almost every
mistake people make with it comes from one of two facts:

1. **512 MB is the binding constraint, not the CPU.** Four cores at 1 GHz are
   enough for real work. Building anything substantial on the board is not
   memory-feasible, and neither is a runtime with a per-core-thread default.
2. **Zero 2 W and Zero W v1 are different architectures.** Getting this wrong
   produces binaries that fail with `Illegal instruction` on first run, or an
   OS image that will not boot at all.

## Step 0 — establish which board and which OS

Never assume. Ask, or check on the board:

```bash
cat /proc/cpuinfo | grep -E 'Model|Hardware'   # "Raspberry Pi Zero 2 W Rev 1.0"
uname -m                                        # aarch64 | armv7l | armv6l
getconf LONG_BIT                                # 64 | 32
```

| | Zero W (v1) | Zero 2 W |
|---|---|---|
| SoC / core | BCM2835, ARM1176JZF-S | BCM2710A1, 4× Cortex-A53 |
| Architecture | **ARMv6** + VFPv2, **no NEON** | **ARMv8-A**, NEON standard |
| RAM | 512 MB | 512 MB |
| Ubuntu | **Not supported, ever** — Ubuntu's floor is ARMv7 | Ubuntu Server **arm64** works |
| Rust target | `arm-unknown-linux-gnueabihf` (ARMv6 build) | `aarch64-unknown-linux-gnu` |
| Wi-Fi | 2.4 GHz 802.11n only | 2.4 GHz 802.11n only |

**The single most common false premise is "Pi Zero W running Ubuntu."** It
cannot exist: Ubuntu dropped ARMv6 long ago. If a user asks for it, say so in
one sentence and offer the two real options (Zero 2 W + Ubuntu, or Zero W +
Raspberry Pi OS), then proceed — do not silently build the wrong thing.

Second most common: Raspberry Pi OS **32-bit** on a Zero 2 W. It boots and
works, but `uname -m` says `armv7l`, so an `aarch64` binary will not run on it.
Match the binary to the *userland*, not to the silicon.

## Step 1 — cross-compile; do not build on the board

Compiling on a Zero 2 W is memory-bound, not patience-bound. A single rustc or
g++ process linking a medium C++ or Rust binary will exceed 512 MB and get
OOM-killed, and adding swap converts the failure into a multi-hour thrash that
also burns the SD card. Cross-compile on a real machine, copy the artifact.

If you truly must build on the board — a small C program, a single Python C
extension — set up zram first (`references/memory.md`), cap parallelism at
`-j2` or `-j1`, and expect minutes. `references/c.md` covers the specifics.

Language-specific cross-compilation, with working toolchain setup:

- **Rust** → `references/rust.md`
- **C / C++** → `references/c.md`
- **Python** (including native wheels, which are the hard part) → `references/python.md`

## Step 2 — size the runtime for 512 MB

Read `references/memory.md` before tuning. The short version:

- Budget roughly: 40-60 MB OS (headless, no desktop), leaving ~430 MB.
- **Set up zram, not a swapfile on the SD card.** zram is compressed RAM swap:
  no card writes, ~3× effective capacity on typical anonymous pages. A swapfile
  on the card is the single biggest cause of "my Pi froze" and of dead cards.
- Cap the service with systemd `MemoryMax=` so an OOM kills *your* process
  predictably instead of the kernel picking a victim (often sshd).
- Prefer SQLite over a database server. A Postgres or MySQL server costs
  60-100 MB RSS before it stores a byte.
- Avoid anything that pulls `torch`, `tensorflow`, `opencv-python`, or
  `pandas` unless you have measured it. Most do not fit, and the ones that do
  leave no headroom.

## Step 3 — protect the SD card

The card is the least reliable part of the board. See `references/sd-card.md`.
The essentials: `noatime`, no swapfile, journald to volatile or capped storage,
SQLite in WAL with `synchronous=NORMAL`, and log rotation with real limits.

## Step 4 — headless setup, service, and access

`references/headless-setup.md` covers first-boot Wi-Fi and SSH without a
monitor (the method differs between Raspberry Pi OS Bookworm and Ubuntu — the
old `wpa_supplicant.conf` trick is dead on both), plus a systemd unit template
with the memory and restart settings that matter on this board.

## Reference files

| File | Read it when |
|---|---|
| `references/rust.md` | Cross-compiling Rust, target selection, `cross`, linker setup, profile tuning, tokio sizing |
| `references/python.md` | Python version choice, venv, native wheels, piwheels, cross-building extensions |
| `references/c.md` | GCC cross toolchains, `-march`/`-mfpu` flags per board, CMake toolchain files, NEON |
| `references/memory.md` | 512 MB budgeting, zram, systemd limits, measuring real usage |
| `references/sd-card.md` | Write reduction, filesystem and journald settings, wear diagnosis |
| `references/headless-setup.md` | First boot Wi-Fi/SSH, OS image choice, systemd unit template |
| `references/gpio-and-hardware.md` | GPIO/I²C/SPI/PWM from all three languages, including the Bookworm libgpiod change |

## Working rules

- **Verify the architecture before writing a single build command.** One
  `uname -m` prevents the most expensive class of error here.
- **Measure, don't estimate, memory.** `systemd-cgtop`, `smem -k`, and
  `/sys/fs/cgroup/<unit>/memory.peak` give real numbers; `top`'s RSS
  double-counts shared pages across processes.
- **Wi-Fi is 2.4 GHz only and shares the antenna with Bluetooth.** If a task
  involves both sustained Wi-Fi throughput and Bluetooth audio, say so early —
  it is a real coexistence limit, not a configuration bug.
- **Power matters.** Brownouts on a marginal supply present as SD corruption,
  random reboots, and Wi-Fi dropping. Check `vcgencmd get_throttled` (`0x0` is
  clean) before debugging software.
