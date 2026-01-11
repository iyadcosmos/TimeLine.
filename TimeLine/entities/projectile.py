"""Projectile entities."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from TimeLine import constants
from TimeLine.util.mathx import Vector2


@dataclass
class Projectile:
    pos: Vector2
    vel: Vector2
    damage: float
    owner: str
    radius: float = 4
    pierce: int = 0
    alive: bool = True
    crit: bool = False

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt

    def draw(self, surface: pygame.Surface) -> None:
        color = constants.COLOR_BULLET
        if self.owner == "enemy":
            color = constants.COLOR_DANGER
        if self.crit:
            color = constants.COLOR_ACCENT
        pygame.draw.circle(surface, color, self.pos, self.radius)
