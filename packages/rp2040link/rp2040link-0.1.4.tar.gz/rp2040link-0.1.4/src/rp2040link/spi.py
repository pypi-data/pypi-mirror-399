from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from .waitbox import WaitBox
from .exceptions import Rp2040LinkError

if TYPE_CHECKING:
    from .pico import Pico


@dataclass
class SPIPort:
    pico: "Pico"
    port: int

    def setup(
        self,
        *,
        miso: int,
        mosi: int,
        sck: int,
        hz: int = 500_000,
        cs_list: Optional[List[int]] = None,
        qualify_pins: bool = True,
    ) -> None:
        self.pico._call_first(
            ["set_pin_mode_spi"],
            spi_port=int(self.port),
            miso=int(miso),
            mosi=int(mosi),
            clock_pin=int(sck),
            clk_frequency=int(hz),
            chip_select_list=None if cs_list is None else [int(x) for x in cs_list],
            qualify_pins=bool(qualify_pins),
        )

    def set_format(self, *, bits: int = 8, polarity: int = 0, phase: int = 0) -> None:
        self.pico._call_first(
            ["spi_set_format"],
            spi_port=int(self.port),
            data_bits=int(bits),
            spi_polarity=int(polarity),
            spi_phase=int(phase),
        )

    def cs(self, cs_pin: int, *, select: bool) -> None:
        self.pico._call_first(["spi_cs_control"], int(cs_pin), 0 if select else 1)

    def write(self, data: List[int]) -> None:
        self.pico._call_first(["spi_write_blocking"], [int(x) for x in data], spi_port=int(self.port))

    def read_sync(self, nbytes: int, *, repeated_tx: int = 0, timeout: float = 1.0) -> List[int]:
        box = WaitBox()

        def _cb(data: List[int]) -> None:
            try:
                count = int(data[2])
                payload = [int(x) for x in data[3:3 + count]]
                box.set(payload)
            except Exception as e:
                box.set(e)

        try:
            self.pico._call_first(
                ["spi_read_blocking"],
                int(nbytes),
                spi_port=int(self.port),
                call_back=_cb,
                repeated_tx_data=int(repeated_tx),
            )
        except TypeError:
            self.pico._call_first(
                ["spi_read_blocking"],
                int(nbytes),
                spi_port=int(self.port),
                callback=_cb,
                repeated_tx_data=int(repeated_tx),
            )

        res = box.wait(float(timeout))
        if isinstance(res, Exception):
            raise Rp2040LinkError(f"SPI read error: {res!r}")
        return res


@dataclass
class SPI:
    pico: "Pico"

    def __post_init__(self):
        self.p0 = SPIPort(self.pico, 0)
        self.p1 = SPIPort(self.pico, 1)
