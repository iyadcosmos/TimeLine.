"""Random helpers."""
from __future__ import annotations

import random


def seed_run(seed: int | None = None) -> random.Random:
    rng = random.Random(seed)
    return rng
