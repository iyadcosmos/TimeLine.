"""Global time manipulation system."""
from __future__ import annotations

from dataclasses import dataclass

from TimeLine.constants import SLOW_SCALE, STOP_COOLDOWN, STOP_COST, STOP_DURATION


@dataclass
class TimeCore:
    time_scale: float = 1.0
    slow_active: bool = False
    stop_timer: float = 0.0
    stop_cooldown: float = 0.0
    slow_scale: float = SLOW_SCALE
    stop_duration: float = STOP_DURATION
    stop_cost: float = STOP_COST

    def update(self, dt: float) -> None:
        if self.stop_timer > 0:
            self.stop_timer = max(0.0, self.stop_timer - dt)
        if self.stop_cooldown > 0:
            self.stop_cooldown = max(0.0, self.stop_cooldown - dt)
        if not self.slow_active and self.stop_timer <= 0:
            self.time_scale = 1.0

    def start_slow(self) -> None:
        if self.stop_timer > 0:
            return
        self.slow_active = True
        self.time_scale = self.slow_scale

    def stop_slow(self) -> None:
        if self.stop_timer > 0:
            return
        self.slow_active = False
        self.time_scale = 1.0

    def trigger_stop(self, energy: float) -> tuple[bool, float]:
        if self.stop_cooldown > 0 or energy < self.stop_cost:
            return False, energy
        self.stop_timer = self.stop_duration
        self.stop_cooldown = STOP_COOLDOWN
        self.time_scale = 0.0
        return True, energy - self.stop_cost
