from __future__ import annotations

import argparse
import sys
import time
from typing import Dict

from serial.tools import list_ports

from .pico import Pico


def _parse_pins(s: str):
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def _parse_polarity(s: str) -> Dict[int, str]:
    # format: "14:low,15:high"
    out: Dict[int, str] = {}
    if not s:
        return out
    for item in s.split(","):
        item = item.strip()
        if not item:
            continue
        pin_str, pol = item.split(":")
        out[int(pin_str.strip())] = pol.strip().lower()
    return out


def cmd_ports(_args: argparse.Namespace) -> int:
    for p in list_ports.comports():
        print(f"{p.device}\t{p.description}")
    return 0


def cmd_blink(args: argparse.Namespace) -> int:
    pins = _parse_pins(args.pins)
    pols = _parse_polarity(args.polarity)

    with Pico(com_port=args.port) as pico:
        # setup pins with requested polarities (default low if unspecified)
        for pin in pins:
            pol = pols.get(pin, "low")
            if pol in ("low", "active_low"):
                pico.setup_output.active_low(pin, initial_off=True)
            elif pol in ("high", "active_high"):
                pico.setup_output.active_high(pin, initial_off=True)
            else:
                raise SystemExit(f"Unknown polarity for pin {pin}: {pol}")

        pico.gpio.blink(pins, times=args.times, period_s=args.period)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="rp2040link", description="rp2040link CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ports = sub.add_parser("ports", help="List serial ports")
    p_ports.set_defaults(func=cmd_ports)

    p_blink = sub.add_parser("blink", help="Blink pins" )
    p_blink.add_argument("--pins", required=True, help="Comma-separated GPIO pins, e.g. 14,15")
    p_blink.add_argument("--polarity", default="", help="Per-pin polarity, e.g. 14:low,15:high")
    p_blink.add_argument("--times", type=int, default=20)
    p_blink.add_argument("--period", type=float, default=0.2)
    p_blink.add_argument("--port", default=None, help="Optional explicit serial port" )
    p_blink.set_defaults(func=cmd_blink)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
