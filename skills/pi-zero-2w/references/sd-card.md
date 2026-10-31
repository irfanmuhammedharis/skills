# Protecting the SD card

The card is the least reliable component and the most common cause of a board
that "just stopped working". Every mitigation below is about reducing writes.

## Choose the card

Use an **A1 or A2 rated** card. The A-rating is about random IOPS, which is
what a running OS does, unlike the Class/UHS ratings which describe sequential
video throughput. A 32 GB A1 card outperforms a 128 GB non-A card for this
workload, and cheap no-name cards fail in weeks.

Better still, boot from USB — the Zero 2 W supports USB boot, and a small SSD or
even a decent USB stick is dramatically more durable. It costs the one USB port.

## Mount options

```
# /etc/fstab — add noatime to the root filesystem
PARTUUID=xxxxxxxx-02  /  ext4  defaults,noatime  0  1
```

`noatime` removes a metadata write on *every file read*. It is the single
cheapest win available and has no downside for a server workload. (`relatime`
is the default and is much better than `atime`, but `noatime` is better still.)

Do **not** add `commit=600` or similar without thinking: it batches writes but
widens the window of data loss on a power cut.

## Kill the swapfile

Covered in `memory.md`, repeated because it matters most: a swapfile on the
card is the fastest way to destroy it. Use zram.

## Bound journald

Unbounded journald is the second biggest writer on a typical Pi.

```ini
# /etc/systemd/journald.conf
[Journal]
Storage=volatile        # RAM only — logs lost on reboot, zero card writes
RuntimeMaxUse=32M
# Or, if you need logs to survive reboots:
# Storage=persistent
# SystemMaxUse=64M
# SystemMaxFileSize=8M
```

`Storage=volatile` is right for a device you can reach over the network and
whose logs you ship elsewhere. `persistent` with a hard cap is right when the
board is remote and a post-mortem matters. Pick deliberately; the default
(`auto`, effectively persistent and uncapped to 10% of the filesystem) is the
wrong answer for both.

## Application-level write reduction

- **SQLite:** `journal_mode=WAL` plus `synchronous=NORMAL`. WAL turns commits
  from "rewrite every touched page" into "append to a log"; NORMAL fsyncs at
  checkpoints instead of every commit. The exposure is losing the last few
  transactions on a power cut, never corruption.
- **Log rotation with real limits** — `logrotate` with `size 10M` and
  `rotate 3`, not the distro default of daily-forever.
- **Don't write metrics every second.** Batch to 30 s or 60 s, or push them off
  the device.
- **`PYTHONDONTWRITEBYTECODE=1`** if the code changes often; leave it off if
  startup time matters more (see `python.md`).
- **`/tmp` on tmpfs**, so scratch files never touch the card:

  ```bash
  echo 'tmpfs /tmp tmpfs defaults,noatime,nosuid,size=64M 0 0' | sudo tee -a /etc/fstab
  ```

## Diagnosing wear and corruption

```bash
# Who is writing? (needs root)
sudo iotop -aoP

# Total writes since boot, per device
cat /proc/diskstats | awk '$3=="mmcblk0" {print $10*512/1048576 " MB written"}'

# Filesystem errors already logged
sudo dmesg -T | grep -i -E 'mmc|ext4|I/O error'
```

Read-only remounts (`EXT4-fs error ... Remounting filesystem read-only`) mean
the card or the power supply is failing. Check power first —
`vcgencmd get_throttled` returning anything but `0x0` points at brownouts,
which corrupt cards and are frequently misdiagnosed as card failure.

## Make it recoverable

Assume the card will fail eventually:

- Keep the whole configuration in a git repo or an image you can re-flash.
- Back up application data off-device on a schedule (`sqlite3 db ".backup"` is
  safe on a live database, unlike `cp`).
- Consider a read-only root filesystem with a small writable overlay for
  genuinely unattended deployments — `raspi-config` has an Overlay FS option
  that makes the root immune to power-cut corruption entirely.
