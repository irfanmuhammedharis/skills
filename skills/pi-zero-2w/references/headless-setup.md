# Headless setup and running as a service

## Choosing the image

| Goal | Image |
|---|---|
| Zero 2 W, best package availability, 64-bit Python wheels | **Raspberry Pi OS Lite (64-bit)** |
| Zero 2 W, Ubuntu tooling / matching a fleet | **Ubuntu Server 24.04 LTS arm64** |
| Zero W v1 | **Raspberry Pi OS Lite (32-bit)** — Ubuntu is not an option, ARMv6 |

Always "Lite"/"Server". A desktop image on 512 MB leaves nothing for the
application.

Ubuntu on the Zero 2 W boots noticeably slower and idles ~20-30 MB heavier than
RPi OS Lite, mostly snapd and cloud-init. Both are removable; see `memory.md`.

## First boot without a monitor

**The old `wpa_supplicant.conf`-in-boot trick no longer works** on either
Raspberry Pi OS Bookworm or current Ubuntu. Use the current mechanism.

### Raspberry Pi OS — use Raspberry Pi Imager

In Imager, click the gear/"Edit Settings" before writing:

- hostname, username + password (there is no default `pi`/`raspberry` any more)
- Wi-Fi SSID, password, **and country** — the radio stays disabled without a
  regulatory domain, which presents as "Wi-Fi silently doesn't work"
- Enable SSH, with a public key if you have one

This writes a `firstrun.sh` into the boot partition. It is the supported path;
hand-editing config files is not.

### Ubuntu Server — cloud-init

Mount the boot partition (`system-boot`) and edit `network-config`:

```yaml
version: 2
wifis:
  wlan0:
    dhcp4: true
    optional: true
    access-points:
      "YourSSID":
        password: "YourPassword"
```

and `user-data` for the user and SSH keys. Note Ubuntu's Wi-Fi frequently fails
to come up on the *very first* boot and works on the second — this is a known
cloud-init ordering quirk, not a fault. Give it one reboot before debugging.

Default login is `ubuntu`/`ubuntu`, forced change on first login.

### Finding the board

```bash
ping raspberrypi.local        # mDNS; works if avahi/systemd-resolved is up
nmap -sn 192.168.1.0/24       # fallback: scan the subnet
```

The Zero 2 W is **2.4 GHz only**. If the network is a single SSID with band
steering, the board may fail to associate while every phone works fine.

## Wi-Fi reliability

Power management on the Pi's Wi-Fi causes intermittent multi-second latency
spikes, which look like an application bug. Turn it off:

```bash
sudo iw wlan0 set power_save off
```

Make it persist:

```ini
# /etc/systemd/system/wifi-powersave-off.service
[Unit]
Description=Disable WiFi power saving
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/iw wlan0 set power_save off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Bluetooth and Wi-Fi share one antenna and one radio on this board. Sustained
Wi-Fi throughput plus Bluetooth audio will degrade both — a physical limit, not
a configuration problem.

## systemd unit template

```ini
[Unit]
Description=My application
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
EnvironmentFile=/opt/myapp/.env
ExecStart=/opt/myapp/myapp

Restart=on-failure
RestartSec=10
# Give up after 5 failures in 10 min instead of restart-looping forever on a
# config error — a tight loop on this board is a real CPU and card load.
StartLimitBurst=5
StartLimitIntervalSec=600

# Memory: see memory.md. MemoryHigh gives a reclaim zone before the hard kill.
MemoryHigh=200M
MemoryMax=250M
OOMPolicy=restart

# Hardening. Add ReadWritePaths for every directory the app writes.
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/myapp

# Defaults sized for a server with cores to spare; trim on a 4-core board.
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myapp
journalctl -u myapp -f
```

### Hardware access under `ProtectSystem=strict`

GPIO, I²C, SPI and serial need explicit grants. Add the user to the right
groups (`gpio`, `i2c`, `spi`, `dialout`) and, if `DeviceAllow` is in play:

```ini
DeviceAllow=/dev/gpiochip0 rw
DeviceAllow=/dev/i2c-1 rw
SupplementaryGroups=gpio i2c spi
```

## Power

Use a supply rated **2.5 A at 5 V** with a decent cable. Undervoltage is the
root cause of a large share of "random reboot", "SD corruption" and "Wi-Fi
drops" reports.

```bash
vcgencmd get_throttled     # 0x0 = clean
# bit 0  set: undervoltage now
# bit 16 set: undervoltage has occurred since boot
```

Anything non-zero: fix the power before debugging software.
