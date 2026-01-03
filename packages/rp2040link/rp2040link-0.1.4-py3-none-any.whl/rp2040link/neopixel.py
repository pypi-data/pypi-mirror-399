from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class NeoPixel:
    pico: "Pico"

    def setup(self, *, pin: int = 28, num_pixels: int = 8, fill: Tuple[int, int, int] = (0, 0, 0)) -> None:
        r, g, b = fill
        self.pico._call_first(
            ["set_pin_mode_neopixel"],
            pin_number=int(pin),
            num_pixels=int(num_pixels),
            fill_r=int(r),
            fill_g=int(g),
            fill_b=int(b),
        )

    def set(self, pixel: int, *, r: int, g: int, b: int, auto_show: bool = False) -> None:
        self.pico._call_first(
            ["neo_pixel_set_value", "neopixel_set_value"],
            int(pixel),
            r=int(r), g=int(g), b=int(b),
            auto_show=bool(auto_show),
        )

    def fill(self, *, r: int, g: int, b: int, auto_show: bool = True) -> None:
        self.pico._call_first(
            ["neopixel_fill"],
            r=int(r), g=int(g), b=int(b),
            auto_show=bool(auto_show),
        )

    def clear(self, *, auto_show: bool = True) -> None:
        self.pico._call_first(["neopixel_clear"], auto_show=bool(auto_show))

    def show(self) -> None:
        self.pico._call_first(["neopixel_show"])
