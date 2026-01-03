from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class GPIO:
    """High-level GPIO operations."""
    pico: "Pico"

    def write(self, pin: int, logical_on: bool) -> None:
        pin = int(pin)
        if not self.pico._out_configured.get(pin):
            # auto-setup using default polarity; avoid forcing OFF to prevent flicker
            self.pico._ensure_output(pin, initial_off=False)

        level = self.pico._level(pin, logical_on)
        self.pico._digital_write(pin, level)

    def on(self, pin: int) -> None:
        self.write(pin, True)

    def off(self, pin: int) -> None:
        self.write(pin, False)

    def pulse(self, pin: int, *, on_s: float = 0.2, off_s: float = 0.2, times: int = 1) -> None:
        for _ in range(int(times)):
            self.on(pin);  time.sleep(float(on_s))
            self.off(pin); time.sleep(float(off_s))

    def blink(self, pins: Iterable[int], *, times: int = 20, period_s: float = 0.5) -> None:
        pins = [int(p) for p in pins]
        for p in pins:
            if not self.pico._out_configured.get(p):
                self.pico._ensure_output(p, initial_off=True)

        half = float(period_s) / 2.0
        for _ in range(int(times)):
            for p in pins: self.on(p)
            time.sleep(half)
            for p in pins: self.off(p)
            time.sleep(half)

    def group(self, *pins: int) -> "GPIOGroup":
        return GPIOGroup(self, [int(p) for p in pins])


@dataclass
class GPIOGroup:
    gpio: GPIO
    pins: List[int]

    def on(self) -> None:
        for p in self.pins:
            self.gpio.on(p)

    def off(self) -> None:
        for p in self.pins:
            self.gpio.off(p)

    def blink(self, *, times: int = 20, period_s: float = 0.5) -> None:
        self.gpio.blink(self.pins, times=times, period_s=period_s)
