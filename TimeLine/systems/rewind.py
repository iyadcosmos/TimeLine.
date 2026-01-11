"""Rewind system with snapshot buffer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from TimeLine.constants import REWIND_SECONDS, REWIND_TICK


@dataclass
class Snapshot:
    time: float
    player: dict
    enemies: list[dict]
    bullets: list[dict]
    pickups: list[dict]
    progression: dict


class RewindSystem:
    def __init__(self) -> None:
        self.buffer: List[Snapshot] = []
        self.interval = REWIND_TICK
        self.max_time = REWIND_SECONDS
        self.timer = 0.0

    def reset(self) -> None:
        self.buffer.clear()
        self.timer = 0.0

    def record(self, dt: float, snapshot: Snapshot) -> None:
        self.timer += dt
        if self.timer < self.interval:
            return
        self.timer -= self.interval
        self.buffer.append(snapshot)
        cutoff = snapshot.time - self.max_time
        while self.buffer and self.buffer[0].time < cutoff:
            self.buffer.pop(0)

    def has_data(self) -> bool:
        return len(self.buffer) > 1

    def pop_latest(self) -> Snapshot | None:
        if not self.buffer:
            return None
        return self.buffer.pop()
