from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, TYPE_CHECKING

from .exceptions import Rp2040LinkError
from .enums import Polarity

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class BinaryPin:
    """Single-pin binary helper.

    bit(1) => logical ON
    bit(0) => logical OFF
    """
    pico: "Pico"
    pin: int
    _state: Optional[bool] = None

    def bit(self, b: int) -> None:
        b = 1 if int(b) else 0
        if not self.pico._out_configured.get(self.pin):
            self.pico._ensure_output(self.pin, initial_off=True)

        logical_on = bool(b)
        self.pico.gpio.write(self.pin, logical_on)
        self._state = logical_on

    def on(self) -> None:
        self.bit(1)

    def off(self) -> None:
        self.bit(0)

    def toggle(self) -> None:
        if self._state is None:
            last = self.pico._last_digital.get(self.pin)
            if last is None:
                self._state = False
            else:
                last_level = int(last[0])
                pol = self.pico._out_polarity.get(self.pin, self.pico.default_output_polarity)
                if pol == Polarity.ACTIVE_LOW:
                    self._state = (last_level == 0)
                else:
                    self._state = (last_level == 1)

        self._state = not self._state
        self.pico.gpio.write(self.pin, self._state)

    def pattern(self, bits: str, *, delay_s: float = 0.1) -> None:
        s = bits.strip().replace("_", "")
        if not s or any(c not in "01" for c in s):
            raise Rp2040LinkError("pattern must contain only 0/1 e.g. '1010'")

        for c in s:
            self.bit(1 if c == "1" else 0)
            time.sleep(float(delay_s))

    def stream(self, values: Iterable[int], *, delay_s: float = 0.1) -> None:
        for v in values:
            self.bit(1 if int(v) else 0)
            time.sleep(float(delay_s))


@dataclass
class BinaryBus:
    """Multi-pin bus for bitmask writes."""
    pico: "Pico"
    pins: List[int]
    msb_first: bool = True

    @property
    def width(self) -> int:
        return len(self.pins)

    def write(self, value: int, *, width: Optional[int] = None) -> None:
        if not self.pins:
            raise Rp2040LinkError("Binary bus needs at least one pin.")

        value = int(value)
        w = self.width if width is None else int(width)
        if w <= 0:
            raise Rp2040LinkError("width must be >= 1")
        if w > self.width:
            raise Rp2040LinkError(f"width={w} > bus width={self.width}")

        for p in self.pins[:w]:
            if not self.pico._out_configured.get(p):
                self.pico._ensure_output(p, initial_off=True)

        for i in range(w):
            bit_index = (w - 1 - i) if self.msb_first else i
            bit = (value >> bit_index) & 1
            self.pico.gpio.write(self.pins[i], bool(bit))

    def pattern(self, bits: str) -> None:
        s = bits.strip().replace("_", "")
        if not s or any(c not in "01" for c in s):
            raise Rp2040LinkError("pattern must contain only 0/1 e.g. '0101'")

        w = len(s)
        if w > self.width:
            raise Rp2040LinkError(f"pattern length={w} > bus width={self.width}")

        value = int(s, 2)
        saved = self.msb_first
        try:
            self.msb_first = True
            self.write(value, width=w)
        finally:
            self.msb_first = saved

    def stream(self, values: Iterable[int], *, delay_s: float = 0.1, width: Optional[int] = None) -> None:
        for v in values:
            self.write(int(v), width=width)
            time.sleep(float(delay_s))


@dataclass
class Binary:
    pico: "Pico"

    def pin(self, pin: int) -> BinaryPin:
        return BinaryPin(self.pico, int(pin))

    def pins(self, *pins: int, msb_first: bool = True) -> BinaryBus:
        return BinaryBus(self.pico, [int(p) for p in pins], msb_first=msb_first)
