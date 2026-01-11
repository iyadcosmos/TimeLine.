"""Entry point for TimeLine."""
from __future__ import annotations

import os
import sys

if __package__ in (None, ""):
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from TimeLine.game import GameApp


def main() -> int:
    app = GameApp()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
