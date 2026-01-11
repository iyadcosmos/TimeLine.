"""Collision helpers."""
from __future__ import annotations

import pygame

from TimeLine.util.mathx import Vector2


def circle_hit(pos_a: Vector2, radius_a: float, pos_b: Vector2, radius_b: float) -> bool:
    return pos_a.distance_squared_to(pos_b) <= (radius_a + radius_b) ** 2


def clamp_to_bounds(pos: Vector2, bounds: pygame.Rect) -> Vector2:
    pos.x = max(bounds.left, min(bounds.right, pos.x))
    pos.y = max(bounds.top, min(bounds.bottom, pos.y))
    return pos
