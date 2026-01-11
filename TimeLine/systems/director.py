"""Director for level objectives and scaling."""
from __future__ import annotations

from dataclasses import dataclass
import random

from TimeLine.constants import LEVEL_TIME_RANGE, LEVEL_KILLS_RANGE, LEVEL_COLLECT_RANGE


@dataclass
class Objective:
    kind: str
    target: float
    progress: float = 0.0
    label: str = ""
    extra: dict | None = None

    def is_complete(self) -> bool:
        return self.progress >= self.target


class Director:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.level_index = 1
        self.objective: Objective = self._roll_objective()
        self.bonus_survival = 0.0
        self.bonus_timer = 0.0

    def _roll_objective(self) -> Objective:
        kind = self.rng.choice(["survive", "kill", "kill_type", "combo", "collect"])
        if kind == "survive":
            target = self.rng.randint(*LEVEL_TIME_RANGE)
            label = f"Survive {target}s"
        elif kind == "kill":
            target = self.rng.randint(*LEVEL_KILLS_RANGE)
            label = f"Defeat {int(target)} enemies"
        elif kind == "kill_type":
            target = self.rng.randint(6, 16)
            enemy_type = self.rng.choice(["chaser", "shooter", "dasher", "tank"])
            label = f"Eliminate {int(target)} {enemy_type}s"
        elif kind == "combo":
            target = self.rng.randint(8, 16)
            label = f"Hold combo {int(target)} for 10s"
        else:
            target = self.rng.randint(*LEVEL_COLLECT_RANGE)
            label = f"Collect {int(target)} shards"
        extra = {"enemy_type": enemy_type} if kind == "kill_type" else {}
        return Objective(kind=kind, target=target, progress=0.0, label=label, extra=extra)

    def on_new_level(self) -> None:
        self.objective = self._roll_objective()
        self.bonus_survival = 0.0
        self.bonus_timer = 0.0

    def update(self, dt: float, combo: float) -> None:
        if self.objective.kind == "survive":
            self.objective.progress += dt
        if self.objective.kind == "combo":
            if combo >= self.objective.target:
                self.objective.progress += dt
            else:
                self.objective.progress = max(0.0, self.objective.progress - dt * 0.5)
        if self.objective.is_complete():
            self.bonus_survival += dt

    def on_kill(self, enemy_type: str) -> None:
        if self.objective.kind == "kill":
            self.objective.progress += 1
        if self.objective.kind == "kill_type":
            target_type = self.objective.extra.get("enemy_type")
            if enemy_type == target_type:
                self.objective.progress += 1

    def on_collect(self) -> None:
        if self.objective.kind == "collect":
            self.objective.progress += 1

    def objective_text(self) -> str:
        if self.objective.kind == "combo":
            return f"{self.objective.label} ({int(self.objective.progress)}/10s)"
        return f"{self.objective.label} ({int(self.objective.progress)}/{int(self.objective.target)})"

    def complete_level(self) -> None:
        self.level_index += 1
        self.on_new_level()
