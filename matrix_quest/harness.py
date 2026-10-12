"""Run one trial's checks on a player's file and print the result as JSON.

Usage: python3 harness.py <trial_id> <file>

The game server starts this in a separate process, so whatever the
player's code does (crash, loop forever, call exit()...) the game itself
keeps running.
"""

import json
import signal
import sys
import tempfile
from pathlib import Path
from types import FrameType

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from matrix_quest.forge import ForgeFailure, load  # noqa: E402
from matrix_quest.worlds import find_trial  # noqa: E402


class TookTooLong(Exception):
    """Raised by the alarm when one check runs for too long."""


def _alarm(signum: int, frame: FrameType | None) -> None:
    raise TookTooLong("took more than 8 seconds (an infinite loop?)")


def main() -> None:
    can_alarm = hasattr(signal, "SIGALRM")  # not on Windows
    if can_alarm:
        signal.signal(signal.SIGALRM, _alarm)
    trial = find_trial(sys.argv[1])
    path = Path(sys.argv[2]).resolve()
    report: dict[str, object] = {"load_error": None, "results": []}
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory() as folder:
        try:
            spell = load(path, Path(folder))
        except ForgeFailure as failure:
            report["load_error"] = str(failure)
        else:
            for name, check in trial.checks:
                try:
                    if can_alarm:
                        signal.alarm(8)
                    check(spell)
                except (ForgeFailure, TookTooLong) as failure:
                    results.append({"name": name, "ok": False,
                                    "message": str(failure)})
                except Exception as error:
                    results.append({
                        "name": name, "ok": False,
                        "message": f"unexpected {type(error).__name__}: "
                                   f"{error}"})
                else:
                    results.append({"name": name, "ok": True,
                                    "message": ""})
                finally:
                    if can_alarm:
                        signal.alarm(0)
    report["results"] = results
    print(json.dumps(report))


if __name__ == "__main__":
    main()
