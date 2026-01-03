from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class _ServoWrite:
    pico: "Pico"

    def angle(self, pin: int, deg: int) -> None:
        self.pico._call_first(["servo_write"], int(pin), int(deg))


@dataclass
class Servo:
    pico: "Pico"
    _configured: Dict[int, bool] = None

    def __post_init__(self):
        self._configured = {}
        self.write = _ServoWrite(self.pico)

    def setup(self, pin: int, *, min_pulse: int = 1000, max_pulse: int = 2000) -> None:
        pin = int(pin)
        if not self._configured.get(pin):
            self.pico._call_first(["set_pin_mode_servo"], pin, min_pulse=int(min_pulse), max_pulse=int(max_pulse))
            self._configured[pin] = True
