"""Pause overlay scene."""
from __future__ import annotations

import pygame

from TimeLine import constants
from TimeLine.util.draw import draw_text


class PauseScene:
    def __init__(self, app, run_scene) -> None:
        self.app = app
        self.run_scene = run_scene
        self.font = pygame.font.Font(None, 40)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.manager.change(self.run_scene)

    def update(self, _dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        self.run_scene.render(screen)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "Paused", (screen.get_width() // 2, screen.get_height() // 2),
                  self.font, constants.COLOR_TEXT, align="center")
