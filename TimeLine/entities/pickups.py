"""Pickup entities."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from TimeLine import constants
from TimeLine.util.mathx import Vector2


@dataclass
class Pickup:
    pos: Vector2
    kind: str
    value: float
    radius: float = 7
    alive: bool = True

    def update(self, dt: float) -> None:
        return

    def draw(self, surface: pygame.Surface) -> None:
        color = constants.COLOR_XP if self.kind == "xp" else constants.COLOR_ENERGY
        pygame.draw.circle(surface, color, self.pos, self.radius)
