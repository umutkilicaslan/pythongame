"""Neo's progress, saved in a small JSON file next to the game."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

SAVE_FILE = Path(__file__).resolve().parent.parent / ".matrix_save.json"

RANKS = [(0, "Bluepill"), (1, "Redpill"), (4, "Potential"),
         (8, "Awakened"), (13, "Operator"), (18, "Zion Defender"),
         (23, "Almost the One")]


@dataclass
class Progress:
    xp: int = 0
    fights: list[str] = field(default_factory=list)
    forged: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)

    def rank(self, worlds: int) -> str:
        if len(self.projects) >= worlds:
            return "The One"
        title = RANKS[0][1]
        for needed, name in RANKS:
            if len(self.forged) >= needed:
                title = name
        return title

    def mark(self, kind: str, item: str, xp: int) -> bool:
        """Record an achievement once. Returns True if it was new."""
        done: list[str] = getattr(self, kind)
        if item in done:
            return False
        done.append(item)
        self.xp += xp
        return True


def load() -> Progress:
    try:
        return Progress(**json.loads(SAVE_FILE.read_text()))
    except FileNotFoundError:
        return Progress()
    except (json.JSONDecodeError, TypeError) as error:
        print(f"(Save file damaged, starting fresh: {error})")
        return Progress()


def save(progress: Progress) -> None:
    try:
        SAVE_FILE.write_text(json.dumps(asdict(progress), indent=2))
    except OSError as error:
        print(f"(Could not save progress: {error})")


def reset() -> Progress:
    try:
        SAVE_FILE.unlink()
    except FileNotFoundError:
        pass
    return Progress()
