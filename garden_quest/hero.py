"""The player's hero and the save file."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

SAVE_FILE = Path(__file__).resolve().parent.parent / ".garden_quest_save.json"

RANKS = [
    "Seedling", "Sprout Apprentice", "Root Adept", "Thorn Mage",
    "Grove Warden", "Archdruid of Exceptions", "Garden Guardian",
]


@dataclass
class Hero:
    name: str = "Guardian"
    max_hp: int = 5
    hp: int = 5
    xp: int = 0
    runes: list[str] = field(default_factory=list)
    chapters_done: list[int] = field(default_factory=list)
    forges_done: list[int] = field(default_factory=list)

    @property
    def rank(self) -> str:
        return RANKS[min(len(self.chapters_done), len(RANKS) - 1)]

    def heal(self) -> None:
        self.hp = self.max_hp

    def learn(self, rune: str) -> None:
        if rune not in self.runes:
            self.runes.append(rune)


def save(hero: Hero) -> None:
    try:
        SAVE_FILE.write_text(json.dumps(asdict(hero), indent=2))
    except OSError as error:
        print(f"  (Could not save your progress: {error})")


def load() -> Hero | None:
    """Return the saved hero, or None if there is no valid save."""
    try:
        data = json.loads(SAVE_FILE.read_text())
        return Hero(**data)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, TypeError) as error:
        print(f"  (Your save file looks damaged, starting fresh: {error})")
        return None


def reset() -> None:
    try:
        SAVE_FILE.unlink()
    except FileNotFoundError:
        pass
