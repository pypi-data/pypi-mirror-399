class Rp2040LinkError(RuntimeError):
    """Base exception for rp2040link."""


class Timeout(Rp2040LinkError):
    """Raised when a callback-driven operation times out."""
