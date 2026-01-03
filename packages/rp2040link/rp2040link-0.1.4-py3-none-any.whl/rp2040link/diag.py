from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class Diag:
    pico: "Pico"

    def reset(self) -> None:
        self.pico._call_first(["reset_board"])

    def get_pins(self) -> Any:
        return self.pico._call_first(["get_pico_pins"])
