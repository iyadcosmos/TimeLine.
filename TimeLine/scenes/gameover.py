"""Game over scene."""
from __future__ import annotations

import pygame

from TimeLine import constants, config
from TimeLine.scenes.run import RunScene
from TimeLine.util.draw import draw_text


class GameOverScene:
    def __init__(self, app, stats: dict) -> None:
        self.app = app
        self.stats = stats
        self.font = pygame.font.Font(None, 48)
        self.small = pygame.font.Font(None, 26)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.app.manager.change(RunScene(self.app))
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, _dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(constants.COLOR_BG)
        draw_text(screen, "RUN FAILED", (config.WIDTH // 2, 90), self.font,
                  constants.COLOR_DANGER, align="midtop")
        draw_text(screen, f"Score: {self.stats.get('score', 0)}", (config.WIDTH // 2, 170),
                  self.small, constants.COLOR_TEXT, align="midtop")
        draw_text(screen, f"Level: {self.stats.get('level', 1)}", (config.WIDTH // 2, 200),
                  self.small, constants.COLOR_TEXT, align="midtop")
        draw_text(screen, f"Enemies defeated: {self.stats.get('kills', 0)}", (config.WIDTH // 2, 230),
                  self.small, constants.COLOR_TEXT, align="midtop")
        draw_text(screen, "Enter: restart | Esc: quit", (config.WIDTH // 2, 320),
                  self.small, constants.COLOR_TEXT, align="midtop")
