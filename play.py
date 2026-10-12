#!/usr/bin/env python3
"""Matrix Quest - learn four Python projects as Neo.

    python3 play.py                 open the game in your browser
    python3 play.py --no-browser    just print the address
    python3 play.py --reset         forget your progress
    python3 play.py --check w2 .    check a real project from the terminal
                                    (w1 Code Cultivation, w2 Garden
                                    Guardian, w3 Data Quest, w4 Data
                                    Archivist)
"""

import argparse
import sys
import webbrowser
from pathlib import Path

from matrix_quest import progress
from matrix_quest.checker import check_project
from matrix_quest.server import serve
from matrix_quest.worlds import WORLDS, find_world


def check_in_terminal(world_id: str, folder: str) -> bool:
    try:
        world = find_world(world_id)
    except KeyError:
        print(f"Unknown world {world_id!r}. Choose one of: "
              + ", ".join(f"{w.id} ({w.project})" for w in WORLDS))
        return False
    root = Path(folder).resolve()
    print(f"Checking {world.project} in {root}\n")
    all_ok = True
    for report in check_project(root, world.exercises):
        all_ok = all_ok and not report.failed
        exercise = report.exercise
        print(("[OK] " if not report.failed else "[!!] ")
              + f"{exercise.folder}/{exercise.filename}")
        for found, mark in ((report.passed, "  ✓ "),
                            (report.failed, "  ✗ "), (report.notes, "  • ")):
            for line in found:
                print(mark + line)
    return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Matrix Quest")
    parser.add_argument("--port", type=int, default=8042)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--reset", action="store_true",
                        help="forget your saved progress")
    parser.add_argument("--check", nargs=2, metavar=("WORLD", "FOLDER"),
                        help="check a real project and exit")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        print("Matrix Quest needs Python 3.10 or newer.")
        return
    if args.reset:
        progress.reset()
        print("Progress reset.")
    if args.check:
        sys.exit(0 if check_in_terminal(*args.check) else 1)
    server, url = serve(args.port, Path.cwd())
    print("\n  Wake up, Neo...  The Matrix is running at:\n")
    print(f"      {url}\n")
    print("  (Press Ctrl+C here to unplug.)\n")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Unplugged. See you in the Matrix.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
