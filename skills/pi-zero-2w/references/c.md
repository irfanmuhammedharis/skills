# C and C++ on the Pi Zero 2 W

C is the one language where you can reasonably build on the board itself — a
few thousand lines compiles in seconds and fits in memory easily. Cross-compile
anyway for anything larger, and always for C++ (template instantiation is what
turns a compile into an OOM kill).

## Toolchains

On a Debian/Ubuntu build host:

```bash
# 64-bit userland (Zero 2 W with RPi OS 64-bit or Ubuntu arm64)
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# 32-bit userland (RPi OS 32-bit on either board)
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
```

The Raspberry Pi Foundation also publishes toolchains, but the Debian ones are
current and adequate. Check the target's glibc before choosing:

```bash
ssh pi@board 'ldd --version | head -1'
```

If your build host's glibc is newer than the board's, dynamically linked
binaries fail at load with `GLIBC_2.xx not found`. Options: build in a
container matching the board's distro release (simplest), link statically
(`-static`), or use a sysroot copied from the board with `--sysroot=`.

## Optimisation flags per board

```bash
# Zero 2 W, 64-bit userland — NEON and crypto are baseline, nothing to enable
aarch64-linux-gnu-gcc -O2 -mcpu=cortex-a53 ...

# Zero 2 W, 32-bit userland
arm-linux-gnueabihf-gcc -O2 -mcpu=cortex-a53 -mfpu=neon-fp-armv8 -mfloat-abi=hard ...

# Zero W v1 — ARMv6, VFPv2, NO NEON
arm-linux-gnueabihf-gcc -O2 -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard ...
```

Passing `-mfpu=neon` for the Zero W v1 is the classic way to produce a binary
that runs for a while and then dies with `Illegal instruction` at the first
vectorised loop. There is no NEON on ARM1176 — the flag compiles, the CPU does
not.

`-O2` over `-O3` is usually right: `-O3`'s extra inlining and unrolling grows
the binary and the instruction footprint, and the A53's caches are small
(32 KB L1, 512 KB shared L2). Measure before assuming `-O3` helps.

`-march=native` is meaningless when cross-compiling and dangerous when building
on the board only if you then copy the binary elsewhere. Prefer explicit
`-mcpu=`.

## CMake toolchain file

```cmake
# aarch64-pi.cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER   aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
set(CMAKE_C_FLAGS   "-mcpu=cortex-a53" CACHE STRING "")
set(CMAKE_CXX_FLAGS "-mcpu=cortex-a53" CACHE STRING "")

# If you have a sysroot copied from the board:
# set(CMAKE_SYSROOT /path/to/pi-sysroot)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

```bash
cmake -B build -DCMAKE_TOOLCHAIN_FILE=aarch64-pi.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
```

## Getting a sysroot

For anything linking against libraries installed on the board:

```bash
mkdir -p ~/pi-sysroot
rsync -avz --delete \
  pi@board:/lib pi@board:/usr/lib pi@board:/usr/include \
  ~/pi-sysroot/
# Absolute symlinks inside the sysroot point at the host's /lib; fix them:
find ~/pi-sysroot -type l -lname '/*' -printf '%p %l\n' | \
  while read l t; do ln -sf "$HOME/pi-sysroot$t" "$l"; done
```

Then `--sysroot=$HOME/pi-sysroot` on both compile and link lines.

## Building on the board

Fine for small C projects. Two rules:

```bash
make -j2          # not -j4: four g++ processes will not fit in 512 MB
```

and set up zram first (`memory.md`). For C++ specifically, `-j1` and
`-fno-var-tracking-assignments` can be the difference between a build that
finishes and one that gets OOM-killed at the last translation unit.

## Calling C from the other two languages

Often the best use of C on this board: keep the orchestration in Python or
Rust and put the hot loop in C.

**From Python** — `ctypes` needs no build step beyond the shared object:

```c
// fast.c  ->  gcc -O2 -shared -fPIC -mcpu=cortex-a53 fast.c -o libfast.so
int sum_u8(const unsigned char *p, int n) {
    int s = 0; for (int i = 0; i < n; i++) s += p[i]; return s;
}
```

```python
import ctypes
lib = ctypes.CDLL("./libfast.so")
lib.sum_u8.restype = ctypes.c_int
lib.sum_u8.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
```

`cffi` is nicer for anything non-trivial; a full CPython extension module is
rarely worth the cross-build cost here.

**From Rust** — a `build.rs` with the `cc` crate compiles C for whatever target
Cargo is building, so it cross-compiles with no extra setup:

```rust
// build.rs
fn main() {
    cc::Build::new().file("src/fast.c").opt_level(2).compile("fast");
}
```

## Real-time-ish work

The Pi runs a normal kernel, not `PREEMPT_RT`. You can get reliable millisecond
scheduling, not microsecond. If a deadline matters:

- `SCHED_FIFO` via `sched_setscheduler`, priority well below 99, plus
  `mlockall(MCL_CURRENT|MCL_FUTURE)` to keep pages resident.
- Pin to a core with `sched_setaffinity` and keep the other three for
  everything else.
- Never `SCHED_FIFO` a thread that can spin — a runaway RT thread on a 4-core
  board locks you out of ssh.

For genuinely tight timing (sub-100 µs), use the hardware: PWM, SPI DMA, or a
microcontroller alongside the Pi.
