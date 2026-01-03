from __future__ import annotations

import threading
from typing import Any, Optional

from .exceptions import Timeout


class WaitBox:
    """Thread-safe wait-for-one-result container."""

    def __init__(self):
        self._ev = threading.Event()
        self._lock = threading.Lock()
        self._value: Any = None

    def set(self, v: Any) -> None:
        with self._lock:
            self._value = v
            self._ev.set()

    def wait(self, timeout: Optional[float]) -> Any:
        if not self._ev.wait(timeout):
            raise Timeout("Timeout waiting for callback result.")
        with self._lock:
            return self._value
