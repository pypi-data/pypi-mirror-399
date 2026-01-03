from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class Inputs:
    pico: "Pico"

    def enable_digital(self, pin: int) -> None:
        self.pico._call_first(["enable_digital_reporting"], int(pin))

    def disable_digital(self, pin: int) -> None:
        self.pico._call_first(["disable_digital_reporting"], int(pin))

    def enable_analog(self, adc_number: int) -> None:
        self.pico._call_first(["enable_analog_reporting"], int(adc_number))

    def disable_analog(self, adc_number: int) -> None:
        self.pico._call_first(["disable_analog_reporting"], int(adc_number))

    def last_digital(self, pin: int) -> Optional[Tuple[int, float]]:
        return self.pico._last_digital.get(int(pin))

    def last_adc(self, adc_number: int) -> Optional[Tuple[int, float]]:
        return self.pico._last_analog.get(int(adc_number))
