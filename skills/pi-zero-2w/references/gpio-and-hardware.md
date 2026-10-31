# GPIO and hardware from Rust, Python and C

## The Bookworm change you will hit first

Raspberry Pi OS Bookworm removed the legacy `/dev/gpiomem` + `sysfs`
(`/sys/class/gpio`) interfaces in favour of **libgpiod** and `/dev/gpiochip*`.
Most tutorials online predate this. Symptoms of following an old one: `RPi.GPIO`
raising `RuntimeError: Cannot determine SOC peripheral base address`, or sysfs
exports silently doing nothing.

On Bookworm and Ubuntu 24.04, use libgpiod (or a library built on it).

Also note: on Bookworm the chip that carries the 40-pin header is
`gpiochip0` on Pi 4 and earlier — but tooling that guesses can pick the wrong
chip. Check:

```bash
gpiodetect              # lists chips and their labels
gpioinfo | head -30     # line names per chip
```

## Enabling the buses

```bash
sudo raspi-config nonint do_i2c 0      # 0 = enable
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial_hw 0
sudo reboot
```

On Ubuntu (no raspi-config), edit `/boot/firmware/config.txt` directly:

```ini
dtparam=i2c_arm=on
dtparam=spi=on
enable_uart=1
```

Verify: `ls /dev/i2c-* /dev/spidev*`, and `i2cdetect -y 1` to scan.

Group membership avoids running as root:

```bash
sudo usermod -aG gpio,i2c,spi,dialout $USER   # log out and back in
```

## Python

```bash
sudo apt install python3-libgpiod python3-gpiozero
```

`gpiozero` is the right default — a friendly API over a pluggable backend, and
it works on Bookworm:

```python
from gpiozero import LED, Button
from signal import pause

led = LED(17)          # BCM numbering
button = Button(2)
button.when_pressed = led.on
button.when_released = led.off
pause()
```

For I²C, `smbus2`; for SPI, `spidev`. Both have wheels for aarch64.

Avoid `RPi.GPIO` on Bookworm — it is unmaintained against the new kernel
interface. `rpi-lgpio` is a drop-in replacement if you must keep the API.

## Rust

```toml
[dependencies]
rppal = "0.19"        # GPIO, I2C, SPI, PWM, UART — no C dependency
```

`rppal` is pure Rust, so it cross-compiles with no sysroot work:

```rust
use rppal::gpio::Gpio;
use std::{thread, time::Duration};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut pin = Gpio::new()?.get(17)?.into_output();
    loop {
        pin.toggle();
        thread::sleep(Duration::from_millis(500));
    }
}
```

Alternatives: `gpiod` (bindings to libgpiod, needs the C library for the
target), `linux-embedded-hal` if you want the `embedded-hal` traits so driver
crates work unchanged.

## C

libgpiod v2 changed the API from v1 — check which you have (`gpiod_chip_open`
vs `gpiod_chip_open_by_name`), since v1 examples are everywhere and will not
compile against v2 headers.

```bash
sudo apt install libgpiod-dev
```

```c
#include <gpiod.h>
// v2 API
struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip0");
// ... request lines via gpiod_line_request / gpiod_line_config
gpiod_chip_close(chip);
```

```bash
gcc -O2 -mcpu=cortex-a53 blink.c -lgpiod -o blink
```

For I²C/SPI from C, the kernel interfaces (`linux/i2c-dev.h`,
`linux/spi/spidev.h`) with `ioctl` are stable and need no library.

## Timing expectations

Userspace GPIO on a non-RT kernel gives reliable **milliseconds**, not
microseconds. Rough ceilings on this board:

| Approach | Realistic max toggle rate |
|---|---|
| Python + gpiozero | ~10-20 kHz, jittery |
| C or Rust, libgpiod/rppal | ~1-2 MHz burst, jitter under load |
| Hardware PWM | exact, up to MHz |
| SPI with DMA | exact, driven by the peripheral |

For anything needing hard timing — WS2812 LEDs, precise pulse trains,
bit-banged protocols at rate — use the hardware peripherals (PWM, SPI, PIO-like
tricks) or pair the Pi with a microcontroller. Bit-banging in a loop and hoping
the scheduler cooperates does not work reliably on a shared 4-core board.

## Camera

The Zero 2 W has a CSI connector (narrow flex — needs the mini-to-standard
adapter cable). On Bookworm the stack is `libcamera` / `picamera2`; the old
`raspistill`/`picamera` stack is gone.

```bash
sudo apt install python3-picamera2
rpicam-hello --list-cameras       # was libcamera-hello on older releases
```

Beware memory: capturing at full resolution into numpy on 512 MB is tight.
Set a modest resolution in the configuration rather than downscaling after
capture.
