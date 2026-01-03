from __future__ import annotations

import time
import atexit
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from .exceptions import Rp2040LinkError
from .enums import Polarity
from .utils import call_first

from .setup_output import SetupOutput
from .gpio import GPIO
from .setup_input import SetupInput
from .inputs import Inputs
from .binary import Binary
from .pwm import PWM
from .servo import Servo
from .neopixel import NeoPixel
from .i2c import I2C
from .spi import SPI
from .diag import Diag


@dataclass
class Pico:
    """Main controller object."""

    com_port: Optional[str] = None
    shutdown_on_exception: bool = False
    default_output_polarity: Polarity = Polarity.ACTIVE_LOW

    # convenience:
    # - auto_open: connect immediately in __post_init__
    # - lazy_open: if True, accessing `.board` will auto-connect
    auto_open: bool = False
    lazy_open: bool = False
    register_atexit_close: bool = True

    _board: Any = field(default=None, init=False, repr=False)

    # output registries
    _out_polarity: Dict[int, Polarity] = field(default_factory=dict, init=False, repr=False)
    _out_configured: Dict[int, bool] = field(default_factory=dict, init=False, repr=False)

    # last seen values: {pin/adc: (value, timestamp)}
    _last_digital: Dict[int, Tuple[int, float]] = field(default_factory=dict, init=False, repr=False)
    _last_analog: Dict[int, Tuple[int, float]] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        # subsystems
        self.setup_output = SetupOutput(self)
        self.gpio = GPIO(self)
        self.setup_input = SetupInput(self)
        self.inputs = Inputs(self)
        self.binary = Binary(self)
        self.pwm = PWM(self)
        self.servo = Servo(self)
        self.neopixel = NeoPixel(self)
        self.i2c = I2C(self)
        self.spi = SPI(self)
        self.diag = Diag(self)

        if self.auto_open:
            self.open()

    # ---------- context manager ----------
    def __enter__(self) -> "Pico":
        return self.open()

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False

    # ---------- connect/disconnect ----------
    def connect(self) -> "Pico":
        """Alias for open()."""
        return self.open()

    def disconnect(self) -> None:
        """Alias for close()."""
        self.close()

    @property
    def is_open(self) -> bool:
        return self._board is not None

    def open(self) -> "Pico":
        if self._board is not None:
            return self

        try:
            from telemetrix_rpi_pico import telemetrix_rpi_pico
        except Exception as e:
            raise Rp2040LinkError("telemetrix-rpi-pico is not installed. Run: pip install telemetrix-rpi-pico") from e

        kwargs = {"shutdown_on_exception": self.shutdown_on_exception}
        if self.com_port:
            kwargs["com_port"] = self.com_port

        self._board = telemetrix_rpi_pico.TelemetrixRpiPico(**kwargs)
        if self.register_atexit_close:
            try:
                atexit.register(self.close)
            except Exception:
                pass
        return self

    def close(self) -> None:
        if self._board is None:
            return

        # best-effort: turn off configured outputs
        for pin in list(self._out_configured.keys()):
            try:
                self.gpio.off(pin)
            except Exception:
                pass

        # best-effort: stop reporting if available
        if hasattr(self._board, "disable_all_reporting"):
            try:
                self._board.disable_all_reporting()
            except Exception:
                pass

        try:
            self._board.shutdown()
        except Exception:
            pass

        self._board = None
        self._out_polarity.clear()
        self._out_configured.clear()
        self._last_digital.clear()
        self._last_analog.clear()

    @property
    def board(self) -> Any:
        if self._board is None:
            if self.lazy_open:
                self.open()
            else:
                raise Rp2040LinkError("Pico is not open. Use open()/connect() or `with Pico(...) as pico:`")
        return self._board

    # ---------- internal helpers ----------
    def _call_first(self, method_names, *args, **kwargs):
        return call_first(self.board, method_names, *args, **kwargs)

    def _polarity(self, pin: int) -> Polarity:
        return self._out_polarity.get(int(pin), self.default_output_polarity)

    def _level(self, pin: int, logical_on: bool) -> int:
        pol = self._polarity(pin)
        if pol == Polarity.ACTIVE_LOW:
            return 0 if logical_on else 1
        return 1 if logical_on else 0

    def _digital_write(self, pin: int, level: int) -> None:
        pin = int(pin)
        level = 1 if int(level) else 0
        self._call_first(["digital_write"], pin, level)
        self._last_digital[pin] = (level, time.time())

    def _ensure_output(self, pin: int, *, initial_off: bool) -> None:
        """Configure pin as digital output (once) + optionally force safe OFF."""
        pin = int(pin)

        if not self._out_configured.get(pin):
            self._call_first(["set_pin_mode_digital_output"], pin)
            self._out_configured[pin] = True

        # critical safety: Telemetrix may default LOW after mode set
        if initial_off:
            self._digital_write(pin, self._level(pin, False))
            time.sleep(0.02)
