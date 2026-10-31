# Rust on the Pi Zero 2 W

## Target selection

| Board + userland | Rust target | Notes |
|---|---|---|
| Zero 2 W, Ubuntu Server arm64 or RPi OS 64-bit | `aarch64-unknown-linux-gnu` | The default choice. NEON is baseline, no extra flags. |
| Zero 2 W, RPi OS 32-bit (`uname -m` = `armv7l`) | `armv7-unknown-linux-gnueabihf` | Very common by accident — check the userland, not the chip. |
| Zero W v1, RPi OS 32-bit | `arm-unknown-linux-gnueabihf` | ARMv6 + VFPv2. See the ARMv6 section below; the stock target is *not* ARMv6-safe out of the box on all toolchains. |

A binary for the wrong one dies with `Illegal instruction` the moment it hits
an unsupported instruction — which may be minutes into the run, not at startup,
so "it launched fine" proves nothing.

## Cross-compiling: `cross` (easiest, needs Docker/Podman)

```bash
cargo install cross --git https://github.com/cross-rs/cross
cross build --release --target aarch64-unknown-linux-gnu
```

`cross` runs the build in a container with the right sysroot and linker already
wired. Use it unless you need system libraries the container image lacks — then
add them via a `Cross.toml` `pre-build` step rather than abandoning `cross`:

```toml
# Cross.toml
[target.aarch64-unknown-linux-gnu]
pre-build = [
  "dpkg --add-architecture arm64",
  "apt-get update && apt-get install -y libssl-dev:arm64 libasound2-dev:arm64",
]
```

## Cross-compiling: native toolchain (no container)

On a Debian/Ubuntu build host:

```bash
sudo apt install gcc-aarch64-linux-gnu
rustup target add aarch64-unknown-linux-gnu
```

`.cargo/config.toml` in the project:

```toml
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
```

Then `cargo build --release --target aarch64-unknown-linux-gnu`.

For the 32-bit targets substitute `gcc-arm-linux-gnueabihf` and
`arm-linux-gnueabihf-gcc`.

## Avoid C dependencies, or plan for them

Pure-Rust crates cross-compile with zero setup. Anything binding a C library
needs that library's headers for the target architecture, which is where most
of the pain lives.

The two that come up constantly:

- **TLS** — use `rustls` (`reqwest` with `default-features = false,
  features = ["rustls-tls"]`), not `native-tls`/`openssl`. This removes the
  need for a cross OpenSSL entirely. If you cannot, `openssl = { version = "0.10",
  features = ["vendored"] }` builds OpenSSL from source for the target.
- **SQLite** — `sqlx`'s `sqlite` feature and `rusqlite`'s `bundled` feature both
  compile SQLite from vendored C, so the target needs no `libsqlite3-dev`.

## Release profile

```toml
[profile.release]
lto = "fat"          # affordable: it costs build-host time, not board time
codegen-units = 1
opt-level = 3        # not "z" — see below
strip = "symbols"    # smaller binary, faster load, less to read on the device
```

**`opt-level = 3` vs `"z"`:** pick `3` when there is any hot loop — DSP, image
or audio processing, parsing at rate. `"z"` disables the vectorisation that
makes NEON worth having on the A53. Pick `"z"` only when the binary is large,
mostly cold, and you are short on flash. Binary size is rarely the real
constraint on a Pi; RSS is, and they are not the same number.

**`panic = "abort"`** saves size and unwind tables, but think before using it in
a long-running service: under `unwind` a panic in one tokio task kills that
task, under `abort` it kills the process. On a headless board that difference is
"one request failed" versus "systemd restart plus cold-start latency".

Also worth setting so debug builds are usable on the board at all:

```toml
[profile.dev.package."*"]
opt-level = 2        # optimise dependencies even in dev
```

## tokio sizing — the thing people miss

`#[tokio::main]` builds a multi-thread runtime with **one worker per core** and
a **512-thread** blocking-pool ceiling. On four cores and 512 MB, build it by
hand:

```rust
fn main() -> std::process::ExitCode {
    let rt = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(2)              // not 4: see below
        .thread_stack_size(512 * 1024)  // tokio's default is 2 MiB
        .max_blocking_threads(16)       // not 512
        .enable_all()
        .build()
        .expect("runtime");
    rt.block_on(async { /* ... */ });
    std::process::ExitCode::SUCCESS
}
```

Fewer workers than cores is usually right on this board. The cost of extra
workers is not CPU but stacks, run queues, and cross-core cache traffic on
whatever latency-sensitive path you have. Leave cores free for the neighbours
that actually need them (PipeWire's RT thread, the Wi-Fi driver's softirqs).

For a single-threaded workload use `new_current_thread()` and skip the work
stealing entirely.

## Deploying

```bash
# Build host
cargo build --release --target aarch64-unknown-linux-gnu
scp target/aarch64-unknown-linux-gnu/release/myapp pi@raspberrypi.local:/tmp/

# Board
sudo install -m 755 /tmp/myapp /usr/local/bin/myapp
sudo systemctl restart myapp
```

Confirm the binary matches the board before chasing a phantom bug:

```bash
file /usr/local/bin/myapp     # "ELF 64-bit LSB ... ARM aarch64"
ldd  /usr/local/bin/myapp     # every library must resolve
```

A glibc-version mismatch shows up here as `version 'GLIBC_2.38' not found`.
Fix it by building against a sysroot no newer than the board's (`ldd --version`
on the board), or by targeting `aarch64-unknown-linux-musl` for a static
binary — musl is the reliable escape hatch when the build host is newer than
the target.

## ARMv6 (Zero W v1) specifics

Rust's `arm-unknown-linux-gnueabihf` target has historically been built for
ARMv6+VFPv2 and works on the Zero W, but toolchain and distro combinations vary.
If you get `Illegal instruction`, pin the ISA explicitly:

```toml
# .cargo/config.toml
[target.arm-unknown-linux-gnueabihf]
linker = "arm-linux-gnueabihf-gcc"
rustflags = ["-C", "target-cpu=arm1176jzf-s", "-C", "target-feature=+vfp2"]
```

Expect no NEON, so autovectorisation gains vanish; algorithms matter more than
flags there. Also expect much slower TLS handshakes — there is no crypto
extension on ARM1176 — which is worth measuring if the workload is
connection-heavy.
