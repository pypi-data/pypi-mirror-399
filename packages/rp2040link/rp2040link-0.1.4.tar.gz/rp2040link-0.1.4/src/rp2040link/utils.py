from __future__ import annotations

from typing import Any, List, Optional


def call_first(board: Any, method_names: List[str], *args, **kwargs):
    """Call the first available method name on `board`.

    Telemetrix has historically had minor naming variations across releases.
    This helper provides best-effort compatibility without hiding real errors.
    """
    last_err: Optional[Exception] = None
    for name in method_names:
        if hasattr(board, name):
            try:
                return getattr(board, name)(*args, **kwargs)
            except TypeError as e:
                last_err = e
                continue

    if last_err is not None:
        raise last_err
    raise AttributeError(f"No matching method on Telemetrix board: {method_names}")
