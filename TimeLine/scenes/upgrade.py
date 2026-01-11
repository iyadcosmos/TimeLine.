"""Upgrade selection scene."""
from __future__ import annotations

import pygame

from TimeLine import constants
from TimeLine.util.draw import draw_text
from TimeLine.systems.ui import UISystem


class UpgradeScene:
    def __init__(self, app, run_scene, cards: list[dict]) -> None:
        self.app = app
        self.run_scene = run_scene
        self.cards = cards
        self.ui = UISystem(app.screen)
        self.font = pygame.font.Font(None, 30)
        self.selected = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.selected = 0
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.selected = 1
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.selected = 2
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(event.pos):
                    self.selected = idx
        if self.selected is not None:
            card = self.cards[self.selected]
            self.run_scene.apply_upgrade(card)
            self.app.manager.change(self.run_scene)

    def update(self, _dt: float) -> None:
        return

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(constants.COLOR_BG)
        draw_text(screen, "Choose Upgrade", (screen.get_width() // 2, 60), self.font,
                  constants.COLOR_TIME, align="midtop")
        self.card_rects = self.ui.draw_upgrade_cards(self.cards)
        draw_text(screen, "Press 1-3 or click", (screen.get_width() // 2, screen.get_height() - 40),
                  self.font, constants.COLOR_TEXT, align="midtop")
