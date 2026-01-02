from __future__ import annotations

import random
import time
from typing import Callable


def sleep_backoff(attempt: int, base: float = 0.6, cap: float = 6.0) -> None:
    # Exponential backoff with jitter
    delay = min(cap, base * (2 ** attempt))
    delay = delay * (0.7 + random.random() * 0.6)  # jitter
    time.sleep(delay)


def safe_float(x, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default
