"""Enemy entities."""
from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from TimeLine import constants
from TimeLine.util.mathx import Vector2


@dataclass
class Enemy:
    pos: Vector2
    enemy_type: str
    vel: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    radius: float = 14
    hp: float = 20
    speed: float = constants.ENEMY_BASE_SPEED
    shoot_timer: float = 0.0
    dash_timer: float = 0.0
    telegraph_timer: float = 0.0
    alive: bool = True

    def configure(self) -> None:
        if self.enemy_type == "chaser":
            self.radius = 14
            self.hp = 26
            self.speed = constants.ENEMY_BASE_SPEED + 25
        elif self.enemy_type == "shooter":
            self.radius = 15
            self.hp = 28
            self.speed = constants.ENEMY_BASE_SPEED - 10
            self.shoot_timer = 1.2
        elif self.enemy_type == "dasher":
            self.radius = 16
            self.hp = 34
            self.speed = constants.ENEMY_BASE_SPEED + 10
            self.telegraph_timer = 1.4
        elif self.enemy_type == "tank":
            self.radius = 22
            self.hp = 80
            self.speed = constants.ENEMY_BASE_SPEED - 30

    def update(self, dt: float, player_pos: Vector2) -> None:
        if self.enemy_type == "shooter":
            self._update_shooter(dt, player_pos)
        elif self.enemy_type == "dasher":
            self._update_dasher(dt, player_pos)
        else:
            self._update_chaser(dt, player_pos)

    def _update_chaser(self, dt: float, player_pos: Vector2) -> None:
        direction = (player_pos - self.pos)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.vel = direction * self.speed
        self.pos += self.vel * dt

    def _update_shooter(self, dt: float, player_pos: Vector2) -> None:
        offset = player_pos - self.pos
        dist = offset.length() if offset.length_squared() > 0 else 0.0
        if dist > 180:
            direction = offset.normalize()
            self.vel = direction * self.speed
        elif dist < 120:
            direction = (-offset).normalize()
            self.vel = direction * self.speed
        else:
            self.vel *= 0.9
        self.pos += self.vel * dt
        self.shoot_timer = max(0.0, self.shoot_timer - dt)

    def _update_dasher(self, dt: float, player_pos: Vector2) -> None:
        if self.telegraph_timer > 0:
            self.telegraph_timer = max(0.0, self.telegraph_timer - dt)
            self.vel *= 0.92
            self.pos += self.vel * dt
            if self.telegraph_timer == 0:
                direction = (player_pos - self.pos)
                if direction.length_squared() > 0:
                    direction = direction.normalize()
                self.vel = direction * (self.speed * 4.0)
                self.dash_timer = 0.25
            return
        if self.dash_timer > 0:
            self.dash_timer = max(0.0, self.dash_timer - dt)
            self.pos += self.vel * dt
            if self.dash_timer == 0:
                self.telegraph_timer = 1.2
            return
        self._update_chaser(dt, player_pos)

    def take_damage(self, amount: float) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def wants_to_shoot(self) -> bool:
        return self.enemy_type == "shooter" and self.shoot_timer <= 0

    def reset_shoot(self) -> None:
        self.shoot_timer = 1.8

    def draw(self, surface: pygame.Surface) -> None:
        if self.enemy_type == "chaser":
            points = [
                (self.pos.x, self.pos.y - self.radius),
                (self.pos.x - self.radius, self.pos.y + self.radius),
                (self.pos.x + self.radius, self.pos.y + self.radius),
            ]
            pygame.draw.polygon(surface, constants.COLOR_ENEMY, points)
        elif self.enemy_type == "shooter":
            rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
            rect.center = self.pos
            pygame.draw.rect(surface, constants.COLOR_SHOOTER, rect)
        elif self.enemy_type == "dasher":
            points = [
                (self.pos.x, self.pos.y - self.radius),
                (self.pos.x - self.radius, self.pos.y),
                (self.pos.x, self.pos.y + self.radius),
                (self.pos.x + self.radius, self.pos.y),
            ]
            pygame.draw.polygon(surface, constants.COLOR_DASHER, points)
            if self.telegraph_timer > 0:
                pygame.draw.circle(surface, constants.COLOR_DANGER, self.pos, self.radius + 10, 1)
        else:
            pygame.draw.circle(surface, constants.COLOR_TANK, self.pos, self.radius)
