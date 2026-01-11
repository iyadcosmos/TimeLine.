"""Enemy spawner and patterns."""
from __future__ import annotations

import random

import pygame

from TimeLine.constants import MAX_ENEMIES


class Spawner:
    def __init__(self, rng: random.Random, bounds: pygame.Rect) -> None:
        self.rng = rng
        self.bounds = bounds
        self.timer = 0.0
        self.interval = 2.0

    def update(self, dt: float, level_index: int, current_count: int) -> bool:
        if current_count >= MAX_ENEMIES:
            return False
        self.timer += dt
        base_interval = max(0.4, self.interval - level_index * 0.05)
        if self.timer >= base_interval:
            self.timer = 0.0
            return True
        return False

    def pick_type(self, level_index: int) -> str:
        weights = ["chaser", "shooter", "dasher", "tank"]
        bias = min(0.4, level_index * 0.05)
        roll = self.rng.random()
        if roll < 0.45:
            return "chaser"
        if roll < 0.7:
            return "shooter"
        if roll < 0.9 - bias:
            return "dasher"
        return "tank"

    def spawn_position(self) -> tuple[float, float]:
        side = self.rng.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return self.rng.uniform(0, self.bounds.width), -30
        if side == "bottom":
            return self.rng.uniform(0, self.bounds.width), self.bounds.height + 30
        if side == "left":
            return -30, self.rng.uniform(0, self.bounds.height)
        return self.bounds.width + 30, self.rng.uniform(0, self.bounds.height)
