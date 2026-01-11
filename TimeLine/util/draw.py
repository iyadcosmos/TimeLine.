"""Drawing helpers for UI and effects."""
from __future__ import annotations

import pygame

from .mathx import clamp


def draw_text(surface: pygame.Surface, text: str, pos: tuple[int, int], font: pygame.font.Font,
              color: tuple[int, int, int], align: str = "topleft") -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(**{align: pos})
    surface.blit(rendered, rect)
    return rect


def draw_bar(surface: pygame.Surface, rect: pygame.Rect, value: float, max_value: float,
             back_color: tuple[int, int, int], fill_color: tuple[int, int, int],
             outline_color: tuple[int, int, int] | None = None) -> None:
    pygame.draw.rect(surface, back_color, rect)
    ratio = 0.0 if max_value <= 0 else clamp(value / max_value, 0.0, 1.0)
    fill_rect = pygame.Rect(rect.x, rect.y, int(rect.width * ratio), rect.height)
    pygame.draw.rect(surface, fill_color, fill_rect)
    if outline_color:
        pygame.draw.rect(surface, outline_color, rect, 1)


def draw_card(surface: pygame.Surface, rect: pygame.Rect, title: str, body: str,
              rarity: str, font: pygame.font.Font, small_font: pygame.font.Font,
              colors: dict[str, tuple[int, int, int]]) -> None:
    base_color = colors.get(rarity, colors["common"])
    pygame.draw.rect(surface, (18, 20, 30), rect)
    pygame.draw.rect(surface, base_color, rect, 2)
    title_rect = draw_text(surface, title, (rect.centerx, rect.y + 10), font, base_color, align="midtop")
    lines = body.split("\n")
    y = title_rect.bottom + 8
    for line in lines:
        draw_text(surface, line, (rect.centerx, y), small_font, (220, 226, 240), align="midtop")
        y += small_font.get_linesize() + 2
