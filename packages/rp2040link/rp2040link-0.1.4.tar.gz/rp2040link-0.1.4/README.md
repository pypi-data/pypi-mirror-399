# rp2040link

**rp2040link** is a high-level, polarity-aware Python controller for **Raspberry Pi Pico / RP2040** boards from a host computer.

It is designed for the workflow you described:

- Flash a **resident firmware** to the Pico (a “server” that stays online),
- Then control the Pico’s pins from the PC with a clean Python API over **USB serial**.

> **Powered by**: rp2040link builds on the proven **Telemetrix-RPi-Pico** stack (host-side Python + Pico-side firmware) and provides a more ergonomic, modern, and safer API layer on top.

---

## Why rp2040link?

Telemetrix is excellent, but you often want a more “application-shaped” interface:
- **Per-pin polarity** (active-low vs active-high) without stringly-typed APIs
- Safe startup (force outputs to a known **OFF** state)
- Binary/bitmask writing to 1 pin or a pin bus
- Convenience helpers: blink, pulse, groups, sync I2C/SPI reads, etc.

rp2040link is exactly that: a **thin, ergonomic layer** over Telemetrix.

---

## Requirements

- Python **3.9+**
- A Raspberry Pi Pico / RP2040 board
- Telemetrix Pico firmware flashed (UF2)
- USB data cable

---

## Install

```bash
pip install rp2040link
```

---

## Flash the Pico (Telemetrix UF2)

Telemetrix requires a small Pico “server” firmware (UF2). Steps (high-level):

1. Hold **BOOTSEL** while plugging the Pico into USB (it appears as a drive like `RPI-RP2`).
2. Drag & drop the Telemetrix UF2 onto the drive.
3. The board reboots and should appear as a serial device (Linux: `/dev/ttyACM*`, macOS: `/dev/cu.*`, Windows: COM port).

If you are unsure which UF2 to use, check Telemetrix-RPi-Pico documentation for the current UF2 builds.

---

## Quick Start

### Mixed polarity outputs (the style you asked for)

```python
import time
from rp2040link import Pico

GP14, GP15 = 14, 15

with Pico() as pico:
    pico.setup_output.active_low(GP14, initial_off=True)    # ON=0 OFF=1
    pico.setup_output.active_high(GP15, initial_off=True)   # ON=1 OFF=0

    pico.gpio.on(GP14); time.sleep(0.5); pico.gpio.off(GP14)
    pico.gpio.on(GP15); time.sleep(0.5); pico.gpio.off(GP15)

    pico.gpio.blink([GP14, GP15], times=20, period_s=0.2)
```

---

## Binary helpers (single pin + bus)

### Single pin (very simple)

```python
from rp2040link import Pico
import time

with Pico() as pico:
    pico.setup_output.active_low(14, initial_off=True)

    b = pico.binary.pin(14)
    b.bit(1); time.sleep(0.2)
    b.bit(0); time.sleep(0.2)
    b.pattern("101001", delay_s=0.05)
```

### Bus (bitmask write)

```python
from rp2040link import Pico
import time

with Pico() as pico:
    pico.setup_output.active_low(14, initial_off=True)
    pico.setup_output.active_high(15, initial_off=True)

    bus = pico.binary.pins(14, 15)  # msb_first=True by default
    bus.write(0b10); time.sleep(0.3)
    bus.write(0b01); time.sleep(0.3)
    bus.stream([0,1,2,3,2,1,0], delay_s=0.15)
```

---

## CLI

rp2040link ships with a small CLI for quick checks:

```bash
rp2040link ports
rp2040link blink --pins 14,15 --polarity 14:low,15:high --times 20 --period 0.2
```

---

## Troubleshooting

### “No such file or directory: /dev/ttyACM0”
- The Pico is likely still in **BOOTSEL** mode (shows as `RPI-RP2` drive) OR
- The cable is charge-only (no data) OR
- The port is not `/dev/ttyACM0` (use `rp2040link ports`).

### Permission denied (Linux)
Add your user to `dialout` and re-login:

```bash
sudo usermod -aG dialout $USER
```

---

## Project layout

- `src/rp2040link/` : library code
- `examples/`       : runnable examples
- `tests/`          : unit tests (hardware-free)
- `docs/`           : docs assets

---

## Development

```bash
pip install -e ".[dev]"
pytest
```

Build distributions:

```bash
python -m build
```

---

## License

MIT — see [LICENSE](LICENSE).


---

## Publishing

See [PUBLISHING.md](PUBLISHING.md) for step-by-step instructions (Trusted Publishing via GitHub OIDC or manual Twine upload).


### Without `with` (manual connect/close)

```python
from rp2040link import Pico
import time

pico = Pico()
try:
    pico.open()  # or pico.connect()

    pico.setup_output.active_low(14, initial_off=True)
    pico.gpio.on(14); time.sleep(1); pico.gpio.off(14)
finally:
    pico.close()  # or pico.disconnect()
```

### Auto-connect options

- `Pico(auto_open=True)` connects in `__post_init__`.
- `Pico(lazy_open=True)` connects automatically on first access to `.board`.

```python
pico = Pico(auto_open=True)     # connects immediately
# or:
pico = Pico(lazy_open=True)     # connects on first operation that touches `.board`
```
