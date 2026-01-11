"""Main menu scene."""
from __future__ import annotations

import pygame

from TimeLine import config, constants
from TimeLine.scenes.run import RunScene
from TimeLine.util.draw import draw_text


class MenuScene:
    def __init__(self, app) -> None:
        self.app = app
        self.font = pygame.font.Font(None, 52)
        self.small_font = pygame.font.Font(None, 24)
        self.buttons: dict[str, pygame.Rect] = {}

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.app.manager.change(RunScene(self.app))
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_f:
                config.FULLSCREEN_DEFAULT = not config.FULLSCREEN_DEFAULT
                flags = pygame.FULLSCREEN if config.FULLSCREEN_DEFAULT else 0
                self.app.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), flags)
            elif event.key == pygame.K_MINUS:
                config.MOUSE_SENSITIVITY = max(0.5, config.MOUSE_SENSITIVITY - 0.1)
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                config.MOUSE_SENSITIVITY = min(2.0, config.MOUSE_SENSITIVITY + 0.1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.buttons.get("start") and self.buttons["start"].collidepoint(pos):
                self.app.manager.change(RunScene(self.app))
            if self.buttons.get("quit") and self.buttons["quit"].collidepoint(pos):
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, _dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(constants.COLOR_BG)
        draw_text(screen, "TIME LINE", (config.WIDTH // 2, 80), self.font, constants.COLOR_TIME, align="midtop")
        draw_text(screen, "Arcade loop shooter", (config.WIDTH // 2, 140), self.small_font,
                  constants.COLOR_TEXT, align="midtop")
        self.buttons["start"] = self._draw_button(screen, "Start Run", 220)
        self.buttons["quit"] = self._draw_button(screen, "Quit", 280)
        draw_text(screen, f"Mouse sensitivity: {config.MOUSE_SENSITIVITY:.1f} (+/-)",
                  (config.WIDTH // 2, 340), self.small_font, constants.COLOR_TEXT, align="midtop")
        draw_text(screen, "F: Fullscreen", (config.WIDTH // 2, 365), self.small_font,
                  constants.COLOR_TEXT, align="midtop")
        draw_text(screen, "Move: WASD/ZQSD | Shoot: LMB | Shift: Rewind", (config.WIDTH // 2, 410),
                  self.small_font, constants.COLOR_TEXT, align="midtop")
        draw_text(screen, "Q: Slow | E: Stop | Space: Dash | F/R: Anchor", (config.WIDTH // 2, 435),
                  self.small_font, constants.COLOR_TEXT, align="midtop")

    def _draw_button(self, screen: pygame.Surface, label: str, y: int) -> pygame.Rect:
        rect = pygame.Rect(0, 0, 200, 40)
        rect.center = (config.WIDTH // 2, y)
        pygame.draw.rect(screen, (22, 26, 38), rect)
        pygame.draw.rect(screen, constants.COLOR_TIME, rect, 2)
        draw_text(screen, label, rect.center, self.small_font, constants.COLOR_TEXT, align="center")
        return rect
