# Fitting into 512 MB

## The budget

Measured on a headless Zero 2 W with nothing extra installed:

| | RSS |
|---|---|
| Kernel + userland, Raspberry Pi OS Lite | ~35-45 MB |
| Kernel + userland, Ubuntu Server minimal | ~55-75 MB (snapd is most of the gap) |
| `sshd` per active session | ~5 MB |
| **Left for your application** | **~420-450 MB** |

Ubuntu Server's `snapd` is worth removing on this board if nothing needs it:

```bash
sudo systemctl disable --now snapd.service snapd.socket snapd.seeded.service
sudo apt purge -y snapd
```

`unattended-upgrades` is the other common surprise — it can spike well over
100 MB during an apt run and has OOM-killed plenty of services on this board.
Either disable it or accept that your service needs `Restart=on-failure`.

## zram, not a swapfile

**This is the single most important tuning step.** A swapfile on the SD card
turns memory pressure into hours of thrashing and burns write cycles. zram is a
compressed block device in RAM: swapping to it costs CPU (cheap on four cores)
instead of I/O, and typical anonymous pages compress ~3:1.

Raspberry Pi OS ships `zram-tools`; on Ubuntu install it:

```bash
sudo apt install zram-tools
```

```ini
# /etc/default/zramswap
ALGO=zstd          # lz4 if CPU is scarcer than RAM; zstd compresses better
PERCENT=50         # 256 MB of RAM -> ~750 MB effective with 3:1 compression
PRIORITY=100
```

```bash
sudo systemctl restart zramswap
swapon --show      # /dev/zram0 should be listed with priority 100
```

Then disable any card-backed swap:

```bash
sudo dphys-swapfile swapoff && sudo systemctl disable dphys-swapfile   # RPi OS
sudo swapoff /swap.img && sudo rm /swap.img                            # Ubuntu
```

With zram in place, raise the kernel's willingness to use it — the default
`swappiness` is tuned for slow disks, and zram is not slow:

```bash
echo 'vm.swappiness=100' | sudo tee /etc/sysctl.d/99-zram.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.d/99-zram.conf
```

## Cap your service so the OOM killer is predictable

Without a limit, the kernel picks the victim by heuristic and frequently
chooses `sshd` — leaving a board that is technically alive and practically
unreachable. Give systemd the limit instead:

```ini
[Service]
MemoryMax=250M          # hard ceiling: exceeded -> this cgroup gets OOM-killed
MemoryHigh=200M         # soft: reclaim aggressively above this, no kill
Restart=on-failure
RestartSec=10
OOMPolicy=restart
```

`MemoryHigh` below `MemoryMax` gives a pressure zone where the kernel reclaims
hard before anything dies — often enough to ride out a transient spike.

Protect sshd explicitly so you can always get in:

```ini
# /etc/systemd/system/ssh.service.d/oom.conf
[Service]
OOMScoreAdjust=-900
```

## Measuring for real

`top`'s RSS double-counts shared pages, so summing it across processes
over-reports badly. Use:

```bash
# Per-cgroup, live — the number systemd actually enforces on
systemd-cgtop -m

# Peak since start, per unit
cat /sys/fs/cgroup/system.slice/myapp.service/memory.peak

# Proportional set size: shared pages divided among sharers. The honest number.
sudo apt install smem && smem -k -t -P myapp

# What the kernel thinks is available (not "free" — available)
free -h
```

`MemAvailable` in `/proc/meminfo` is the figure to watch; `free` can look
alarmingly low while `available` is fine because page cache is counted as used.

## Diagnosing an OOM kill

```bash
journalctl -k | grep -i -E 'killed process|oom'
journalctl -u myapp -n 50
dmesg -T | grep -i oom
```

The kernel line names the victim, its RSS at death, and the cgroup. If the
victim is not your process, your process is probably the *cause* — check its
peak.

## Application-level rules

- **One process, not a worker pool.** Each Python worker or Node cluster child
  is a full runtime copy. Prefer async concurrency inside one process.
- **Bound every buffer and queue.** An unbounded channel is an OOM waiting for
  a slow consumer. On this board it will find one.
- **Stream, don't slurp.** Reading a 100 MB file into a `Vec<u8>` is a fifth of
  the machine.
- **Cap HTTP request bodies.** Most frameworks buffer the whole body before a
  handler runs, so the body limit is also an "how much RAM can any client make
  me allocate" limit.
- **Prefer SQLite to a database server.** Postgres is 60-100 MB before storing
  anything; SQLite is a library inside your process with a page cache you set.
- **Watch thread stacks.** Default 8 MB (glibc) or 2 MiB (tokio) per thread is
  virtual, but each thread that touches its stack makes some of it resident.
  Cut it when spawning many.
