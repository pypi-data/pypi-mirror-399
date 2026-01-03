from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class _PWMWrite:
    pico: "Pico"

    def percent(self, pin: int, duty: int) -> None:
        self.pico._call_first(["pwm_write"], int(pin), duty_cycle=int(duty), raw=False)

    def raw(self, pin: int, duty: int) -> None:
        self.pico._call_first(["pwm_write"], int(pin), duty_cycle=int(duty), raw=True)


@dataclass
class PWM:
    pico: "Pico"
    _configured: Dict[int, bool] = None

    def __post_init__(self):
        self._configured = {}
        self.write = _PWMWrite(self.pico)

    def setup(self, pin: int) -> None:
        pin = int(pin)
        if not self._configured.get(pin):
            self.pico._call_first(["set_pin_mode_pwm_output"], pin)
            self._configured[pin] = True
