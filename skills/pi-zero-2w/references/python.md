# Python on the Pi Zero 2 W

Python is the easiest of the three to get running and the easiest to blow the
memory budget with. The two things that matter are **which wheels exist for
your architecture** and **how much the interpreter plus its imports cost**.

## Interpreter and environment

Use the system Python. Building CPython from source on the board takes hours
and gains nothing; on a build host it needs a cross-build setup that is rarely
worth it.

| OS | Default Python |
|---|---|
| Raspberry Pi OS Bookworm | 3.11 |
| Ubuntu Server 24.04 arm64 | 3.12 |
| Ubuntu Server 22.04 arm64 | 3.10 |

Bookworm and Ubuntu both mark the system Python as
[PEP 668](https://peps.python.org/pep-0668/) externally-managed, so `pip install`
outside a venv fails by design. Always:

```bash
python3 -m venv --system-site-packages ~/.venvs/app
~/.venvs/app/bin/pip install -U pip wheel
```

`--system-site-packages` matters on a Pi: it lets the venv see apt-installed
packages that are painful to build from source (`python3-numpy`,
`python3-gpiozero`, `python3-libgpiod`, `python3-picamera2`).

Baseline cost: a bare CPython 3.11 process is ~9-12 MB RSS. `import numpy`
adds ~25 MB. `import pandas` adds ~90 MB. `import torch` adds ~350 MB and will
not co-exist with anything else on this board.

## Wheels — the actual difficulty

A package with C extensions needs a wheel matching the architecture, or it
builds from source on the board (slow, and often OOM-killed).

Check what you will get *before* installing:

```bash
python3 -c "import sysconfig; print(sysconfig.get_platform())"
# linux-aarch64        -> manylinux_*_aarch64 wheels apply
# linux-armv7l         -> few manylinux wheels exist; piwheels matters
# linux-armv6l         -> essentially no manylinux wheels; piwheels only
```

**64-bit (`aarch64`) is a completely different experience from 32-bit here.**
PyPI has `manylinux2014_aarch64` wheels for numpy, scipy, cryptography, pillow,
lxml, pydantic-core, orjson and most of the ecosystem. On 32-bit ARM there are
almost none, and you fall back to piwheels or source builds. If a project is
Python-heavy and the board is a Zero 2 W, **run a 64-bit OS** — this is the
single highest-leverage choice available.

### piwheels (Raspberry Pi OS only)

Raspberry Pi OS ships `/etc/pip.conf` pointing at piwheels, a prebuilt ARM
wheel index. It is why `pip install numpy` is fast on RPi OS 32-bit and slow on
a plain Ubuntu armhf install. On Ubuntu you can opt in:

```ini
# ~/.venvs/app/pip.conf  (or /etc/pip.conf)
[global]
extra-index-url=https://www.piwheels.org/simple
```

piwheels builds for `cp39`/`cp311` armv6l/armv7l tags. It does **not** serve
aarch64 — on 64-bit, PyPI's own manylinux aarch64 wheels are what you want, and
adding piwheels does nothing.

### When a source build is unavoidable

```bash
sudo apt install python3-dev build-essential libffi-dev
# and whatever the package needs: libjpeg-dev, libxml2-dev, libssl-dev, ...
```

Then follow the memory rules in `memory.md` — set up zram first, and expect a
single-file C extension build to still take minutes. If it OOMs, build the
wheel on a build host (`pip wheel` inside an `aarch64` container via
`docker run --platform linux/arm64`) and `scp` the `.whl` across.

## Package choices that fit

| Instead of | Use | Why |
|---|---|---|
| `pandas` | `sqlite3` + plain dicts, or `polars` if a wheel exists | pandas is ~90 MB resident before your data |
| `requests` | `httpx` or `urllib3` | smaller import graph; `requests` is fine if already present |
| `opencv-python` | `picamera2` + `numpy`, or `opencv-python-headless` | the non-headless build pulls a full GUI stack |
| `torch` / `tensorflow` | `tflite-runtime`, `onnxruntime`, or a cloud API | neither fits usefully in 512 MB |
| Flask/Django + gunicorn workers | a single `uvicorn` worker, or Flask with 1-2 threads | each worker is a full interpreter copy |
| `matplotlib` | render off-device | ~60 MB and a font cache build on first use |

## Running a Python service

Use a venv path directly in the unit — do not rely on `PATH` or shell
activation:

```ini
[Service]
ExecStart=/home/pi/.venvs/app/bin/python -u -m myapp
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONDONTWRITEBYTECODE=1
MemoryMax=200M
```

`-u`/`PYTHONUNBUFFERED` makes logs reach journald immediately rather than
sitting in a 4 KB buffer — without it a crashed service often appears to have
logged nothing at all.

`PYTHONDONTWRITEBYTECODE` avoids `.pyc` writes to the SD card on every import
of a changed file. Leave it **off** if startup time matters more than card
writes: recompiling bytecode every boot is measurably slow on this CPU. Pick
one deliberately.

## Measuring

```bash
/usr/bin/time -v python3 -m myapp 2>&1 | grep 'Maximum resident'
python3 -X importtime -m myapp 2>&1 | tail -20   # slowest imports
```

`-X importtime` is the fastest way to find the accidental 40 MB import someone
added three layers down.

## Async and threads

The GIL means CPU-bound Python uses one of the four cores no matter what you
do. For CPU-bound work, either move it to C (see `c.md`) or use
`multiprocessing` with **at most 2 workers** — each is a full interpreter, so
four workers of a numpy-importing process is ~140 MB of interpreters alone.

For I/O-bound work `asyncio` is nearly free and is the right default here.
