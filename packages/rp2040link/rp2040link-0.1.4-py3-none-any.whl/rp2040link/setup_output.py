from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .enums import Polarity

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class SetupOutput:
    """Attribute-driven output setup.

    Example:
        pico.setup_output.active_low(14, initial_off=True)
        pico.setup_output.active_high(15, initial_off=True)
    """
    pico: "Pico"

    def active_low(self, pin: int, *, initial_off: bool = True) -> None:
        pin = int(pin)
        self.pico._out_polarity[pin] = Polarity.ACTIVE_LOW
        self.pico._ensure_output(pin, initial_off=initial_off)

    def active_high(self, pin: int, *, initial_off: bool = True) -> None:
        pin = int(pin)
        self.pico._out_polarity[pin] = Polarity.ACTIVE_HIGH
        self.pico._ensure_output(pin, initial_off=initial_off)
