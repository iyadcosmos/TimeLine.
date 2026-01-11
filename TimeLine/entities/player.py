"""Player entity."""
from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from TimeLine import constants
from TimeLine.util.mathx import Vector2, clamp


@dataclass
class Player:
    pos: Vector2
    vel: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    radius: float = constants.PLAYER_RADIUS
    max_hp: float = constants.PLAYER_MAX_HP
    hp: float = constants.PLAYER_MAX_HP
    hp_regen: float = 0.0
    max_energy: float = constants.PLAYER_MAX_ENERGY
    energy: float = constants.PLAYER_MAX_ENERGY
    energy_regen: float = constants.PLAYER_ENERGY_REGEN
    fire_rate: float = constants.PLAYER_FIRE_RATE
    bullet_speed: float = constants.PLAYER_BULLET_SPEED
    bullet_damage: float = constants.PLAYER_BULLET_DAMAGE
    bullet_pierce: int = 0
    crit_chance: float = 0.0
    spread: float = 0.0

    dash_cooldown: float = 0.0
    dash_iframes: float = constants.DASH_IFRAMES
    dash_ready: bool = True

    rewind_ready: bool = True
    slow_ready: bool = True
    anchor_ready: bool = True

    invincible_t: float = 0.0
    shoot_timer: float = 0.0
    anchor_cooldown: float = 0.0
    anchor_charges: int = 1

    debug_info: dict = field(default_factory=dict)

    def update(self, dt: float, bounds: pygame.Rect) -> None:
        self.pos += self.vel * dt
        self.pos.x = clamp(self.pos.x, bounds.left + self.radius, bounds.right - self.radius)
        self.pos.y = clamp(self.pos.y, bounds.top + self.radius, bounds.bottom - self.radius)
        if self.invincible_t > 0:
            self.invincible_t = max(0.0, self.invincible_t - dt)
        if self.dash_cooldown > 0:
            self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.dash_ready = self.dash_cooldown <= 0
        if self.anchor_cooldown > 0:
            self.anchor_cooldown = max(0.0, self.anchor_cooldown - dt)
        self.anchor_ready = self.anchor_cooldown <= 0

    def regen_energy(self, dt: float) -> None:
        self.energy = clamp(self.energy + self.energy_regen * dt, 0.0, self.max_energy)
        if self.hp_regen > 0:
            self.hp = clamp(self.hp + self.hp_regen * dt, 0.0, self.max_hp)

    def can_shoot(self, dt: float) -> bool:
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        return self.shoot_timer <= 0

    def reset_shot_timer(self) -> None:
        self.shoot_timer = 1.0 / max(0.1, self.fire_rate)

    def take_damage(self, amount: float) -> None:
        if self.invincible_t > 0:
            return
        self.hp = max(0.0, self.hp - amount)
        self.invincible_t = constants.PLAYER_INVINCIBLE

    def is_dead(self) -> bool:
        return self.hp <= 0

    def heal(self, amount: float) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def apply_upgrade(self, upgrade: dict) -> None:
        upgrade["apply"](self)
