from enum import Enum


class Polarity(Enum):
    """Per-pin logical-to-electrical mapping."""
    ACTIVE_LOW = 0   # ON=0 OFF=1
    ACTIVE_HIGH = 1  # ON=1 OFF=0
