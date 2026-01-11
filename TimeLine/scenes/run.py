"""Main run gameplay scene."""
from __future__ import annotations

import math
import random

import pygame

from TimeLine import config, constants
from TimeLine.entities.player import Player
from TimeLine.entities.enemy import Enemy
from TimeLine.entities.projectile import Projectile
from TimeLine.entities.pickups import Pickup
from TimeLine.entities.effects import Particle, AfterImage
from TimeLine.scenes.gameover import GameOverScene
from TimeLine.scenes.upgrade import UpgradeScene
from TimeLine.scenes.pause import PauseScene
from TimeLine.systems.collision import circle_hit
from TimeLine.systems.director import Director
from TimeLine.systems.progression import Progression
from TimeLine.systems.spawner import Spawner
from TimeLine.systems.timecore import TimeCore
from TimeLine.systems.rewind import RewindSystem, Snapshot
from TimeLine.systems.ui import UISystem
from TimeLine.util.inputmap import InputMap
from TimeLine.util.mathx import Vector2, clamp


class RunScene:
    def __init__(self, app) -> None:
        self.app = app
        self.screen = app.screen
        self.bounds = pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)
        self.player = Player(pos=Vector2(config.WIDTH / 2, config.HEIGHT / 2))
        self.progression = Progression()
        self.timecore = TimeCore()
        self.rng = random.Random()
        self.director = Director(self.rng)
        self.spawner = Spawner(self.rng, self.bounds)
        self.rewind = RewindSystem()
        self.ui = UISystem(self.screen)
        self.inputmap = InputMap()
        self.enemies: list[Enemy] = []
        self.bullets: list[Projectile] = []
        self.pickups: list[Pickup] = []
        self.particles: list[Particle] = []
        self.afterimages: list[AfterImage] = []
        self.rewinding = False
        self.rewind_auto = 0.0
        self.rewind_cost = constants.REWIND_COST
        self.rewind_speed = constants.REWIND_SPEED
        self.rewind.max_time = constants.REWIND_SECONDS
        self.objective_complete = False
        self.kill_count = 0
        self.debug = False
        self.anchor_positions: list[dict] = []
        self.upgrades = self._build_upgrades()
        self.toast("Loop started")

    def toast(self, text: str) -> None:
        self.ui.set_toast(text)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.manager.change(PauseScene(self.app, self))
            elif event.key == pygame.K_TAB:
                self.debug = not self.debug
            elif event.key == pygame.K_e:
                success, energy = self.timecore.trigger_stop(self.player.energy)
                if success:
                    self.player.energy = energy
                    self.progression.add_time_score(30)
                    self.toast("Time stopped")
            elif event.key == pygame.K_SPACE:
                self._dash()
            elif event.key == pygame.K_f:
                self._place_anchor()
            elif event.key == pygame.K_r:
                self._return_anchor()

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed(3)
        mouse_pos = Vector2(pygame.mouse.get_pos())

        if self.rewind_auto > 0:
            self.rewind_auto = max(0.0, self.rewind_auto - dt)
            self.rewinding = True
        if not keys[pygame.K_LSHIFT] and self.rewind_auto <= 0:
            self.rewinding = False

        if not self.rewinding:
            self._handle_movement(keys)
            if keys[pygame.K_q]:
                if self.player.energy > 0:
                    self.timecore.start_slow()
                    self.player.energy = max(0.0, self.player.energy - constants.SLOW_COST * dt)
                else:
                    self.timecore.stop_slow()
            else:
                self.timecore.stop_slow()
        else:
            self.timecore.stop_slow()

        self.timecore.update(dt)
        world_dt = dt * self.timecore.time_scale

        if self.rewinding:
            self._rewind_step(dt)
            return

        self.player.regen_energy(dt)
        self.player.update(dt, self.bounds)
        self._update_anchors(dt)
        self.player.rewind_ready = self.player.energy > 0 and self.rewind.has_data()
        self.player.slow_ready = self.player.energy > 0

        self._update_enemies(world_dt)
        self._update_bullets(world_dt)
        self._update_pickups(world_dt)
        self._update_particles(world_dt)

        if mouse_buttons[0] and self.player.can_shoot(dt):
            self._shoot(mouse_pos)

        self._handle_collisions()
        self._handle_spawns(world_dt)

        self.progression.update(dt)
        self.director.update(dt, self.progression.combo)
        self.ui.update(dt)

        if self.director.objective.is_complete() and not self.objective_complete:
            self.objective_complete = True
            self.toast("Objective complete! Bonus survival")

        if self.director.objective.is_complete() and self.director.bonus_survival > 2.5:
            self._start_upgrade()

        if self.player.is_dead():
            if self.player.energy >= constants.DEATH_REWIND_COST and self.rewind.has_data():
                self.player.energy -= constants.DEATH_REWIND_COST
                self.rewind_auto = 0.9
                self.player.hp = 1
                self.player.invincible_t = 0.6
                self.toast("Death rewound")
            else:
                stats = {
                    "score": self.progression.score,
                    "level": self.director.level_index,
                    "kills": self.kill_count,
                }
                self.app.manager.change(GameOverScene(self.app, stats))

        self._record_snapshot(dt)
        self._update_debug()

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(constants.COLOR_BG)
        self._draw_background(screen)
        drawables = []
        drawables.extend(self.pickups)
        drawables.extend(self.enemies)
        drawables.append(self.player)
        drawables = sorted(drawables, key=lambda obj: obj.pos.y)
        for obj in drawables:
            if isinstance(obj, Player):
                self._draw_player(screen)
            elif isinstance(obj, Enemy):
                obj.draw(screen)
            elif isinstance(obj, Pickup):
                obj.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for particle in self.particles:
            particle.draw(screen)
        for after in self.afterimages:
            after.draw(screen)
        if self.rewinding:
            self.ui.draw_overlay("rewind", 70)
        elif self.timecore.stop_timer > 0:
            self.ui.draw_overlay("stop", 90)
        elif self.timecore.slow_active:
            self.ui.draw_overlay("slow", 55)
        self.ui.draw_hud(self.player, self.progression, self.director, self.timecore, self.debug)

    def _handle_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        direction = Vector2(0, 0)
        if self.inputmap.is_left(keys):
            direction.x -= 1
        if self.inputmap.is_right(keys):
            direction.x += 1
        if self.inputmap.is_up(keys):
            direction.y -= 1
        if self.inputmap.is_down(keys):
            direction.y += 1
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.player.vel = direction * constants.PLAYER_SPEED

    def _shoot(self, mouse_pos: Vector2) -> None:
        direction = (mouse_pos - self.player.pos)
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()
        spread = self.player.spread
        if spread > 0:
            angle = math.radians(random.uniform(-spread, spread))
            direction = Vector2(
                direction.x * math.cos(angle) - direction.y * math.sin(angle),
                direction.x * math.sin(angle) + direction.y * math.cos(angle),
            )
        crit = self.rng.random() < self.player.crit_chance
        damage = self.player.bullet_damage * (1.5 if crit else 1.0)
        bullet = Projectile(
            pos=self.player.pos.copy(),
            vel=direction * self.player.bullet_speed,
            damage=damage,
            owner="player",
            pierce=self.player.bullet_pierce,
            crit=crit,
        )
        self.bullets.append(bullet)
        self.player.reset_shot_timer()

    def _dash(self) -> None:
        if not self.player.dash_ready:
            return
        keys = pygame.key.get_pressed()
        direction = Vector2(0, 0)
        if self.inputmap.is_left(keys):
            direction.x -= 1
        if self.inputmap.is_right(keys):
            direction.x += 1
        if self.inputmap.is_up(keys):
            direction.y -= 1
        if self.inputmap.is_down(keys):
            direction.y += 1
        if direction.length_squared() == 0:
            direction = Vector2(pygame.mouse.get_pos()) - self.player.pos
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()
        self.player.pos += direction * constants.DASH_DISTANCE
        self.player.invincible_t = self.player.dash_iframes
        self.player.dash_cooldown = constants.DASH_COOLDOWN
        self.afterimages.append(AfterImage(self.player.pos.copy(), self.player.radius, 0.3, constants.COLOR_TIME))
        self.progression.add_time_score(10)

    def _place_anchor(self) -> None:
        if not self.player.anchor_ready:
            return
        if len(self.anchor_positions) >= self.player.anchor_charges:
            self.anchor_positions.pop(0)
        self.anchor_positions.append({"pos": self.player.pos.copy(), "age": 0.0})
        self.toast("Anchor placed")

    def _return_anchor(self) -> None:
        if not self.anchor_positions:
            return
        if self.player.energy < constants.ANCHOR_COST:
            return
        anchor = self.anchor_positions.pop()
        self.player.pos = anchor["pos"]
        self.player.energy -= constants.ANCHOR_COST
        self.player.anchor_cooldown = constants.ANCHOR_COOLDOWN
        self.afterimages.append(AfterImage(self.player.pos.copy(), self.player.radius, 0.3, constants.COLOR_TIME))
        self.progression.add_time_score(20)

    def _update_anchors(self, dt: float) -> None:
        for anchor in self.anchor_positions:
            anchor["age"] += dt
        self.anchor_positions = [a for a in self.anchor_positions if a["age"] < constants.ANCHOR_MAX_AGE]

    def _update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            enemy.update(dt, self.player.pos)
            if enemy.enemy_type == "shooter" and enemy.shoot_timer < 0.2:
                self.particles.append(Particle(enemy.pos.copy(), Vector2(0, 0), constants.COLOR_SHOOTER, 4, 0.2, 0.2))
            if enemy.wants_to_shoot():
                direction = (self.player.pos - enemy.pos)
                if direction.length_squared() > 0:
                    direction = direction.normalize()
                bullet = Projectile(enemy.pos.copy(), direction * constants.ENEMY_BULLET_SPEED, 12, "enemy")
                self.bullets.append(bullet)
                enemy.reset_shoot()
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]

    def _update_bullets(self, dt: float) -> None:
        for bullet in self.bullets:
            bullet.update(dt)
            if not self.bounds.collidepoint(bullet.pos.x, bullet.pos.y):
                bullet.alive = False
        self.bullets = [bullet for bullet in self.bullets if bullet.alive]

    def _update_pickups(self, dt: float) -> None:
        for pickup in self.pickups:
            pickup.update(dt)
        self.pickups = [pickup for pickup in self.pickups if pickup.alive]

    def _update_particles(self, dt: float) -> None:
        for particle in self.particles:
            particle.update(dt)
        for after in self.afterimages:
            after.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        self.afterimages = [a for a in self.afterimages if a.life > 0]

    def _handle_collisions(self) -> None:
        for enemy in self.enemies:
            if circle_hit(self.player.pos, self.player.radius, enemy.pos, enemy.radius):
                self.player.take_damage(12)
        for bullet in list(self.bullets):
            if bullet.owner == "player":
                for enemy in self.enemies:
                    if circle_hit(bullet.pos, bullet.radius, enemy.pos, enemy.radius):
                        enemy.take_damage(bullet.damage)
                        if not enemy.alive:
                            self._enemy_killed(enemy)
                        if bullet.pierce > 0:
                            bullet.pierce -= 1
                        else:
                            bullet.alive = False
                        break
            else:
                if circle_hit(self.player.pos, self.player.radius, bullet.pos, bullet.radius):
                    self.player.take_damage(14)
                    bullet.alive = False
        for pickup in self.pickups:
            if circle_hit(self.player.pos, self.player.radius, pickup.pos, pickup.radius):
                pickup.alive = False
                if pickup.kind == "xp":
                    leveled = self.progression.add_xp(pickup.value)
                    if leveled:
                        self.toast("Level up! Upgrade after objective")
                else:
                    self.player.energy = clamp(self.player.energy + pickup.value, 0.0, self.player.max_energy)
                self.director.on_collect()

    def _handle_spawns(self, dt: float) -> None:
        if self.spawner.update(dt, self.director.level_index, len(self.enemies)):
            enemy_type = self.spawner.pick_type(self.director.level_index)
            pos = Vector2(self.spawner.spawn_position())
            enemy = Enemy(pos=pos, enemy_type=enemy_type)
            enemy.configure()
            self.enemies.append(enemy)

    def _enemy_killed(self, enemy: Enemy) -> None:
        self.kill_count += 1
        self.progression.add_score(20)
        self.progression.add_combo(1)
        self.director.on_kill(enemy.enemy_type)
        for _ in range(3):
            vel = Vector2(self.rng.uniform(-80, 80), self.rng.uniform(-80, 80))
            self.particles.append(Particle(enemy.pos.copy(), vel, constants.COLOR_XP, 3, 0.6, 0.6))
        self.pickups.append(Pickup(enemy.pos.copy(), "xp", 8))
        if enemy.enemy_type == "tank":
            self.pickups.append(Pickup(enemy.pos.copy(), "xp", 16))
            self.pickups.append(Pickup(enemy.pos.copy(), "energy", 12))

    def _record_snapshot(self, dt: float) -> None:
        snapshot = Snapshot(
            time=pygame.time.get_ticks() / 1000.0,
            player={
                "pos": (self.player.pos.x, self.player.pos.y),
                "vel": (self.player.vel.x, self.player.vel.y),
                "hp": self.player.hp,
                "energy": self.player.energy,
            },
            enemies=[{
                "pos": (enemy.pos.x, enemy.pos.y),
                "vel": (enemy.vel.x, enemy.vel.y),
                "hp": enemy.hp,
                "type": enemy.enemy_type,
            } for enemy in self.enemies],
            bullets=[{
                "pos": (bullet.pos.x, bullet.pos.y),
                "vel": (bullet.vel.x, bullet.vel.y),
                "owner": bullet.owner,
                "damage": bullet.damage,
                "pierce": bullet.pierce,
            } for bullet in self.bullets],
            pickups=[{
                "pos": (pickup.pos.x, pickup.pos.y),
                "kind": pickup.kind,
                "value": pickup.value,
            } for pickup in self.pickups],
            progression={
                "score": self.progression.score,
                "combo": self.progression.combo,
                "level": self.progression.level,
                "xp": self.progression.xp,
                "xp_next": self.progression.xp_next,
            },
        )
        self.rewind.record(dt, snapshot)

    def _rewind_step(self, dt: float) -> None:
        if self.player.energy <= 0 or not self.rewind.has_data():
            self.rewinding = False
            return
        steps = max(1, int(self.rewind_speed * dt / constants.REWIND_TICK))
        snapshot = None
        for _ in range(steps):
            snapshot = self.rewind.pop_latest()
        if snapshot is None:
            self.rewinding = False
            return
        self.player.energy = max(0.0, self.player.energy - self.rewind_cost * dt)
        self.player.pos = Vector2(snapshot.player["pos"])
        self.player.vel = Vector2(snapshot.player["vel"])
        self.player.hp = snapshot.player["hp"]
        self._restore_entities(snapshot)
        self.afterimages.append(AfterImage(self.player.pos.copy(), self.player.radius, 0.25, constants.COLOR_TIME))

    def _restore_entities(self, snapshot: Snapshot) -> None:
        self.enemies.clear()
        for data in snapshot.enemies:
            enemy = Enemy(pos=Vector2(data["pos"]), enemy_type=data["type"])
            enemy.configure()
            enemy.hp = data["hp"]
            enemy.vel = Vector2(data["vel"])
            self.enemies.append(enemy)
        self.bullets = [
            Projectile(Vector2(data["pos"]), Vector2(data["vel"]), data["damage"], data["owner"],
                       pierce=data["pierce"])
            for data in snapshot.bullets
        ]
        self.pickups = [
            Pickup(Vector2(data["pos"]), data["kind"], data["value"])
            for data in snapshot.pickups
        ]
        self.progression.score = snapshot.progression["score"]
        self.progression.combo = snapshot.progression["combo"]
        self.progression.level = snapshot.progression["level"]
        self.progression.xp = snapshot.progression["xp"]
        self.progression.xp_next = snapshot.progression["xp_next"]

    def _start_upgrade(self) -> None:
        self.objective_complete = False
        self.director.complete_level()
        cards = self._roll_upgrades()
        self.app.manager.change(UpgradeScene(self.app, self, cards))

    def _roll_upgrades(self) -> list[dict]:
        cards = []
        while len(cards) < 3:
            card = self.rng.choice(self.upgrades)
            if card not in cards:
                cards.append(card)
        return cards

    def apply_upgrade(self, card: dict) -> None:
        card["apply"](self)
        self.toast(f"Upgrade: {card['name']}")

    def _build_upgrades(self) -> list[dict]:
        upgrades = []

        def add(name: str, desc: str, rarity: str, apply_fn) -> None:
            upgrades.append({"name": name, "desc": desc, "rarity": rarity, "apply": apply_fn})

        add("Rapid Pulse", "+15% fire rate", "common", lambda r: setattr(r.player, "fire_rate", r.player.fire_rate * 1.15))
        add("Quickload", "+20% bullet speed", "common", lambda r: setattr(r.player, "bullet_speed", r.player.bullet_speed * 1.2))
        add("Pierce 1", "Bullets pierce +1", "rare", lambda r: setattr(r.player, "bullet_pierce", r.player.bullet_pierce + 1))
        add("Critical Path", "+8% crit chance", "rare", lambda r: setattr(r.player, "crit_chance", r.player.crit_chance + 0.08))
        add("Split Arc", "Add slight spread", "common", lambda r: setattr(r.player, "spread", r.player.spread + 3))
        add("Max Integrity", "+20 max HP", "common", lambda r: setattr(r.player, "max_hp", r.player.max_hp + 20))
        add("Regenerator", "+1 HP regen", "rare", lambda r: setattr(r.player, "hp_regen", r.player.hp_regen + 1))
        add("Dash Echo", "+0.06s i-frames", "rare", lambda r: setattr(r.player, "dash_iframes", r.player.dash_iframes + 0.06))
        add("Rewind Efficiency", "-20% rewind cost", "rare",
            lambda r: setattr(r, "rewind_cost", max(6.0, r.rewind_cost * 0.8)))
        add("Rewind Buffer", "+1s buffer", "epic",
            lambda r: setattr(r.rewind, "max_time", r.rewind.max_time + 1.0))
        add("Deep Slow", "Slow to 25%", "epic",
            lambda r: setattr(r.timecore, "slow_scale", max(0.2, r.timecore.slow_scale - 0.1)))
        add("Stop Stretch", "+0.2s time stop", "rare",
            lambda r: setattr(r.timecore, "stop_duration", r.timecore.stop_duration + 0.2))
        add("Anchor Double", "Anchor +1 charge", "rare", lambda r: setattr(r.player, "anchor_charges", r.player.anchor_charges + 1))
        add("Energy Tank", "+25 max energy", "common", lambda r: setattr(r.player, "max_energy", r.player.max_energy + 25))
        add("Energy Flow", "+4 energy regen", "rare", lambda r: setattr(r.player, "energy_regen", r.player.energy_regen + 4))
        add("Combo Drift", "Combo decays slower", "common",
            lambda r: setattr(r.progression, "combo_decay_mult", r.progression.combo_decay_mult * 0.8))
        add("Chrono Score", "+10% time score", "rare",
            lambda r: setattr(r.progression, "time_score_bonus", r.progression.time_score_bonus + 0.1))
        add("Overcharge", "Energy cap +40", "epic", lambda r: setattr(r.player, "max_energy", r.player.max_energy + 40))
        return upgrades

    def _draw_background(self, screen: pygame.Surface) -> None:
        grid_color = constants.COLOR_GRID
        spacing = 40
        offset = (pygame.time.get_ticks() * 0.02) % spacing
        for x in range(-spacing, config.WIDTH + spacing, spacing):
            pygame.draw.line(screen, grid_color, (x + offset, 0), (x + offset, config.HEIGHT), 1)
        for y in range(-spacing, config.HEIGHT + spacing, spacing):
            pygame.draw.line(screen, grid_color, (0, y + offset), (config.WIDTH, y + offset), 1)

    def _draw_player(self, screen: pygame.Surface) -> None:
        color = constants.COLOR_PLAYER
        if self.player.invincible_t > 0:
            color = constants.COLOR_TIME
        pygame.draw.circle(screen, color, self.player.pos, self.player.radius)
        shadow_pos = self.player.pos + Vector2(6, 8)
        pygame.draw.circle(screen, (10, 10, 18), shadow_pos, self.player.radius, 1)
        for anchor in self.anchor_positions:
            pygame.draw.circle(screen, constants.COLOR_TIME, anchor["pos"], 8, 2)

    def _update_debug(self) -> None:
        self.player.debug_info["fps"] = int(self.app.clock.get_fps())
        self.player.debug_info["enemies"] = len(self.enemies)
        self.player.debug_info["bullets"] = len(self.bullets)
