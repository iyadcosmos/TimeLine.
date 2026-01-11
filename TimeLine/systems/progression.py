"""Progression system: XP, score, combo."""
from __future__ import annotations

from dataclasses import dataclass

from TimeLine.constants import COMBO_DECAY, COMBO_MAX


@dataclass
class Progression:
    level: int = 1
    xp: float = 0.0
    xp_next: float = 60.0
    score: int = 0
    combo: float = 0.0
    combo_timer: float = 0.0
    combo_mult: float = 1.0
    combo_decay_mult: float = 1.0
    time_score_bonus: float = 0.0

    def add_score(self, value: int) -> None:
        self.score += int(value * self.combo_mult)

    def add_time_score(self, value: int) -> None:
        bonus = 1.0 + self.time_score_bonus
        self.score += int(value * bonus)

    def add_xp(self, amount: float) -> bool:
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = int(self.xp_next * 1.2 + 15)
            leveled = True
        return leveled

    def add_combo(self, amount: float) -> None:
        self.combo = min(COMBO_MAX, self.combo + amount)
        self.combo_timer = 2.2
        self.combo_mult = 1.0 + self.combo * 0.1

    def update(self, dt: float) -> None:
        if self.combo_timer > 0:
            self.combo_timer = max(0.0, self.combo_timer - dt)
        else:
            decay = COMBO_DECAY * self.combo_decay_mult
            self.combo = max(0.0, self.combo - decay * dt)
            self.combo_mult = 1.0 + self.combo * 0.1
