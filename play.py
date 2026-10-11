#!/usr/bin/env python3
"""Garden Quest - learn Python exceptions by saving an enchanted garden.

    python3 play.py            start (or continue) the adventure
    python3 play.py --fast     no typewriter effect
    python3 play.py --reset    forget your saved progress
    python3 play.py --check .  only run the Final Trial on a project folder
"""

import argparse
import sys
from pathlib import Path

from garden_quest import game, hero, ui
from garden_quest.final_trial import run_final_trial


def main() -> None:
    parser = argparse.ArgumentParser(description="Garden Quest")
    parser.add_argument("--fast", action="store_true",
                        help="disable the typewriter effect")
    parser.add_argument("--reset", action="store_true",
                        help="delete your saved progress")
    parser.add_argument("--check", metavar="FOLDER",
                        help="check your ex0..ex4 project and exit")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        print("Garden Quest needs Python 3.10 or newer.")
        return
    if args.fast:
        ui.SPEED = 0
    if args.reset:
        hero.reset()
        print("Progress reset.")
    if args.check:
        ok = run_final_trial(Path(args.check).resolve())
        sys.exit(0 if ok else 1)
    try:
        game.start()
    except (ui.QuitGame, KeyboardInterrupt):
        print()


if __name__ == "__main__":
    main()
