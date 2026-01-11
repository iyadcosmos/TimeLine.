"""Main game loop and scene manager."""
from __future__ import annotations

import traceback

import pygame

from TimeLine import config
from TimeLine.scenes.menu import MenuScene


class SceneManager:
    def __init__(self, scene) -> None:
        self.scene = scene

    def change(self, scene) -> None:
        self.scene = scene


class GameApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        flags = pygame.FULLSCREEN if config.FULLSCREEN_DEFAULT else 0
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), flags)
        self.clock = pygame.time.Clock()
        self.manager = SceneManager(MenuScene(self))

    def start_run(self) -> None:
        from TimeLine.scenes.run import RunScene

        self.manager.change(RunScene(self))

    def run(self) -> int:
        try:
            return self._run_loop()
        except Exception:
            traceback.print_exc()
            self._show_crash()
            return 1
        finally:
            pygame.quit()

    def _run_loop(self) -> int:
        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.manager.scene.handle_event(event)
            self.manager.scene.update(dt)
            self.manager.scene.render(self.screen)
            pygame.display.flip()
        return 0

    def _show_crash(self) -> None:
        try:
            self.screen.fill((10, 10, 10))
            font = pygame.font.Font(None, 28)
            text = font.render("Crash detected. Check terminal.", True, (220, 90, 90))
            rect = text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
            self.screen.blit(text, rect)
            pygame.display.flip()
            pygame.time.wait(2500)
        except Exception:
            return
