"""Keyboard mapping supporting QWERTY/AZERTY."""
from __future__ import annotations

import pygame


class InputMap:
    def __init__(self) -> None:
        self.move_left = {pygame.K_a, pygame.K_q}
        self.move_right = {pygame.K_d}
        self.move_up = {pygame.K_w, pygame.K_z}
        self.move_down = {pygame.K_s}

    def is_left(self, keys: pygame.key.ScancodeWrapper) -> bool:
        return any(keys[key] for key in self.move_left)

    def is_right(self, keys: pygame.key.ScancodeWrapper) -> bool:
        return any(keys[key] for key in self.move_right)

    def is_up(self, keys: pygame.key.ScancodeWrapper) -> bool:
        return any(keys[key] for key in self.move_up)

    def is_down(self, keys: pygame.key.ScancodeWrapper) -> bool:
        return any(keys[key] for key in self.move_down)
