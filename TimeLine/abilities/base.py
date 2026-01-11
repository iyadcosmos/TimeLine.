"""Ability base classes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ability:
    name: str
    cooldown: float
    timer: float = 0.0

    def update(self, dt: float) -> None:
        if self.timer > 0:
            self.timer = max(0.0, self.timer - dt)

    def ready(self) -> bool:
        return self.timer <= 0

    def trigger(self) -> None:
        self.timer = self.cooldown
