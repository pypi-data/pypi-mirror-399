from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class SetupInput:
    pico: "Pico"

    def _wrap_digital_cb(self, user_cb: Optional[Callable[[List[int]], None]]):
        def _cb(data: List[int]) -> None:
            try:
                pin = int(data[1])
                val = int(data[2])
                ts = float(data[3])
                self.pico._last_digital[pin] = (val, ts)
            except Exception:
                pass
            if user_cb:
                user_cb(data)
        return _cb

    def plain(self, pin: int, *, callback: Optional[Callable[[List[int]], None]] = None) -> None:
        cb = self._wrap_digital_cb(callback)
        self.pico._call_first(["set_pin_mode_digital_input"], int(pin), callback=cb)

    def pullup(self, pin: int, *, callback: Optional[Callable[[List[int]], None]] = None) -> None:
        cb = self._wrap_digital_cb(callback)
        self.pico._call_first(["set_pin_mode_digital_input_pullup"], int(pin), callback=cb)

    def pulldown(self, pin: int, *, callback: Optional[Callable[[List[int]], None]] = None) -> None:
        cb = self._wrap_digital_cb(callback)
        self.pico._call_first(
            ["set_pin_mode_digital_input_pull_down", "set_pin_mode_digital_input_pulldown"],
            int(pin),
            callback=cb,
        )

    def _wrap_analog_cb(self, user_cb: Optional[Callable[[List[int]], None]]):
        def _cb(data: List[int]) -> None:
            try:
                adc = int(data[1])
                val = int(data[2])
                ts = float(data[3])
                self.pico._last_analog[adc] = (val, ts)
            except Exception:
                pass
            if user_cb:
                user_cb(data)
        return _cb

    def adc(self, adc_number: int, *, differential: int = 0, callback: Optional[Callable[[List[int]], None]] = None) -> None:
        cb = self._wrap_analog_cb(callback)
        self.pico._call_first(["set_pin_mode_analog_input"], int(adc_number), differential=int(differential), callback=cb)
