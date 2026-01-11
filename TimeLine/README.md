# TimeLine V1

Arcade top-down shooter built in Pygame, focused on time manipulation.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r TimeLine/requirements.txt
```

## Run

```bash
python -m TimeLine.main
# or
python TimeLine/main.py
```

## Controls

- Move: WASD / ZQSD
- Aim: Mouse
- Shoot: Left Mouse Button (hold)
- Rewind: Shift (hold)
- Slow Time: Q (hold)
- Time Stop: E (tap)
- Dash: Space (tap)
- Anchor: F place / R return
- Pause: Esc
- Debug Overlay: Tab

## Gameplay Loop

Each run is a sequence of short level segments with a clear objective. Complete the objective to open the upgrade selection, then dive into the next loop with rising intensity. Bonus survival time after an objective improves score and XP.

## Time Powers

- **Rewind:** Hold Shift to rewind 4–5 seconds. Costs energy and restores snapshots.
- **Slow Time:** Hold Q to slow the world while you move freely.
- **Time Stop:** Tap E to freeze threats briefly (with cooldown).
- **Dash:** Short invincible dash for quick reposition.
- **Anchor:** Place a temporal marker and return later.

## Roadmap V2

- Temporal Echo (afterimages that shoot)
- Time Split (clone companion)
- Bullet Recall advanced patterns
- Boss: Chrono Warden
- Biomes + visual assets
- Full audio pass
