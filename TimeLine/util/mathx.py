"""Math helpers."""
from __future__ import annotations

from dataclasses import dataclass

import pygame


Vector2 = pygame.math.Vector2


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


@dataclass
class SmoothValue:
    value: float

    def update(self, target: float, speed: float, dt: float) -> float:
        delta = target - self.value
        self.value += delta * min(1.0, speed * dt)
        return self.value
