"""Simple visual effects."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from TimeLine.util.mathx import Vector2


@dataclass
class Particle:
    pos: Vector2
    vel: Vector2
    color: tuple[int, int, int]
    radius: float
    life: float
    max_life: float

    def update(self, dt: float) -> None:
        self.pos += self.vel * dt
        self.life -= dt

    def draw(self, surface: pygame.Surface) -> None:
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        color = (*self.color, alpha)
        gfx = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(gfx, color, (self.radius, self.radius), self.radius)
        surface.blit(gfx, (self.pos.x - self.radius, self.pos.y - self.radius))


@dataclass
class AfterImage:
    pos: Vector2
    radius: float
    life: float
    color: tuple[int, int, int]

    def update(self, dt: float) -> None:
        self.life -= dt

    def draw(self, surface: pygame.Surface) -> None:
        alpha = max(0, min(255, int(180 * (self.life / 0.3))))
        gfx = pygame.Surface((self.radius * 2 + 6, self.radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(gfx, (*self.color, alpha), (gfx.get_width() // 2, gfx.get_height() // 2),
                           self.radius + 2, 2)
        surface.blit(gfx, (self.pos.x - gfx.get_width() // 2, self.pos.y - gfx.get_height() // 2))
