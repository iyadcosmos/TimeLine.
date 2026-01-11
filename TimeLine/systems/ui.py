"""UI system for HUD and overlays."""
from __future__ import annotations

import pygame

from TimeLine import constants
from TimeLine.util.draw import draw_bar, draw_text, draw_card


class UISystem:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        self.tiny_font = pygame.font.Font(None, 16)
        self.toast_timer = 0.0
        self.toast_text = ""
        self.overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    def set_toast(self, text: str, duration: float = 2.0) -> None:
        self.toast_text = text
        self.toast_timer = duration

    def update(self, dt: float) -> None:
        if self.toast_timer > 0:
            self.toast_timer = max(0.0, self.toast_timer - dt)

    def draw_hud(self, player, progression, director, timecore, debug: bool = False) -> None:
        self._draw_bars(player, progression)
        self._draw_objective(director)
        self._draw_score(progression)
        self._draw_abilities(player, timecore)
        if self.toast_timer > 0:
            draw_text(self.screen, self.toast_text, (self.screen.get_width() // 2, 16), self.font,
                      constants.COLOR_ACCENT, align="midtop")
        if debug:
            self._draw_debug(player)

    def _draw_bars(self, player, progression) -> None:
        hp_rect = pygame.Rect(16, 14, 220, 12)
        draw_bar(self.screen, hp_rect, player.hp, player.max_hp,
                 (30, 24, 28), constants.COLOR_DANGER, (60, 60, 80))
        energy_rect = pygame.Rect(16, 32, 220, 10)
        draw_bar(self.screen, energy_rect, player.energy, player.max_energy,
                 (18, 26, 32), constants.COLOR_ENERGY, (60, 60, 80))
        xp_rect = pygame.Rect(16, 48, 220, 8)
        draw_bar(self.screen, xp_rect, progression.xp, progression.xp_next,
                 (20, 22, 34), constants.COLOR_XP, (60, 60, 80))
        draw_text(self.screen, f"Lv {progression.level}", (240, 44), self.tiny_font,
                  constants.COLOR_TEXT, align="midleft")

    def _draw_objective(self, director) -> None:
        draw_text(self.screen, director.objective_text(), (16, 64), self.small_font,
                  constants.COLOR_ACCENT, align="topleft")

    def _draw_score(self, progression) -> None:
        draw_text(self.screen, f"Score {progression.score}", (self.screen.get_width() - 16, 14),
                  self.small_font, constants.COLOR_TEXT, align="topright")
        draw_text(self.screen, f"Combo x{progression.combo:.1f}", (self.screen.get_width() - 16, 32),
                  self.small_font, constants.COLOR_ACCENT, align="topright")

    def _draw_abilities(self, player, timecore) -> None:
        base_x = 16
        base_y = self.screen.get_height() - 36
        spacing = 38
        labels = [
            ("SHIFT", player.rewind_ready),
            ("Q", player.slow_ready),
            ("E", timecore.stop_cooldown <= 0),
            ("SPACE", player.dash_ready),
            ("F", player.anchor_ready),
        ]
        for idx, (label, ready) in enumerate(labels):
            rect = pygame.Rect(base_x + idx * spacing, base_y, 32, 24)
            color = constants.COLOR_TIME if ready else (60, 70, 90)
            pygame.draw.rect(self.screen, (20, 26, 40), rect)
            pygame.draw.rect(self.screen, color, rect, 1)
            draw_text(self.screen, label, rect.center, self.tiny_font, color, align="center")

    def _draw_debug(self, player) -> None:
        fps = int(player.debug_info.get("fps", 0))
        enemies = player.debug_info.get("enemies", 0)
        bullets = player.debug_info.get("bullets", 0)
        text = f"FPS {fps} | Enemies {enemies} | Bullets {bullets}"
        draw_text(self.screen, text, (16, self.screen.get_height() - 16), self.tiny_font,
                  constants.COLOR_TEXT, align="bottomleft")

    def draw_overlay(self, mode: str, alpha: int) -> None:
        self.overlay.fill((0, 0, 0, 0))
        if mode == "slow":
            self.overlay.fill((*constants.COLOR_TIME, alpha))
        elif mode == "stop":
            self.overlay.fill((80, 110, 130, alpha))
        elif mode == "rewind":
            self.overlay.fill((70, 200, 220, alpha))
        self.screen.blit(self.overlay, (0, 0))

    def draw_upgrade_cards(self, cards: list[dict]) -> list[pygame.Rect]:
        width = self.screen.get_width()
        height = self.screen.get_height()
        card_width = 220
        card_height = 220
        margin = 20
        start_x = (width - (card_width * 3 + margin * 2)) // 2
        rects = []
        colors = {
            "common": (120, 210, 220),
            "rare": (180, 150, 255),
            "epic": (255, 180, 90),
        }
        for idx, card in enumerate(cards):
            rect = pygame.Rect(start_x + idx * (card_width + margin), height // 2 - card_height // 2,
                               card_width, card_height)
            draw_card(self.screen, rect, card["name"], card["desc"], card["rarity"],
                      self.font, self.small_font, colors)
            rects.append(rect)
        return rects
