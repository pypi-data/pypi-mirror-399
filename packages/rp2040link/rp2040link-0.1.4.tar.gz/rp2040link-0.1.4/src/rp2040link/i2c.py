from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from .waitbox import WaitBox
from .exceptions import Rp2040LinkError

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class I2CPort:
    pico: "Pico"
    port: int

    def setup(self, *, sda: int, scl: int) -> None:
        self.pico._call_first(["set_pin_mode_i2c"], i2c_port=int(self.port), sda_gpio=int(sda), scl_gpio=int(scl))

    def write(self, address: int, data: List[int], *, no_stop: bool = False) -> None:
        self.pico._call_first(
            ["i2c_write"],
            int(address),
            args=[int(x) for x in data],
            i2c_port=int(self.port),
            no_stop=bool(no_stop),
        )

    def read_sync(
        self,
        address: int,
        register: Optional[int],
        nbytes: int,
        *,
        no_stop: bool = False,
        timeout: float = 1.0,
    ) -> List[int]:
        box = WaitBox()

        def _cb(data: List[int]) -> None:
            try:
                count = int(data[3])
                payload = [int(x) for x in data[4:4 + count]]
                box.set(payload)
            except Exception as e:
                box.set(e)

        try:
            self.pico._call_first(
                ["i2c_read"],
                int(address),
                register if register is None else int(register),
                int(nbytes),
                callback=_cb,
                i2c_port=int(self.port),
                no_stop=bool(no_stop),
            )
        except TypeError:
            # fallback for older signatures
            self.pico.board.i2c_read(int(address), register, int(nbytes), _cb, int(self.port), bool(no_stop))

        res = box.wait(float(timeout))
        if isinstance(res, Exception):
            raise Rp2040LinkError(f"I2C read error: {res!r}")
        return res


@dataclass
class I2C:
    pico: "Pico"

    def __post_init__(self):
        self.p0 = I2CPort(self.pico, 0)
        self.p1 = I2CPort(self.pico, 1)
