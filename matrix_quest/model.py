"""The building blocks of the game: worlds, chapters, riddles, trials."""

from dataclasses import dataclass, field
from typing import Callable

from .forge import Spell

Check = Callable[[Spell], None]


@dataclass
class Line:
    """One line of dialogue in a story scene."""
    who: str
    text: str


@dataclass
class Page:
    """One page of a training program: a bit of text and an example."""
    title: str
    text: list[str]
    code: str = ""


@dataclass
class Riddle:
    """One question of a fight.

    kind "choice": pick one of `options`, `answer` is the index.
    kind "blank":  type a word, `answer` lists accepted words.
    If `run` is True, the operator console replays `code` with real
    Python after the answer, so you can see what really happens.
    """
    question: str
    explain: str
    kind: str = "choice"
    code: str = ""
    options: tuple[str, ...] = ()
    answer: int | tuple[str, ...] = 0
    run: bool = False


@dataclass
class Enemy:
    name: str
    art: str
    taunt: str
    defeat: str


@dataclass
class Trial:
    """A forge trial: the player writes a file, the checks test it."""
    id: str
    filename: str
    mission: list[str]
    skeleton: str
    hints: list[str]
    checks: list[tuple[str, Check]] = field(default_factory=list)
    run_args: str = ""
    run_stdin: str = ""


@dataclass
class Chapter:
    id: str
    title: str
    exercise: str
    concept: str
    story: list[Line]
    pages: list[Page]
    enemy: Enemy
    riddles: list[Riddle]
    trial: Trial
    victory: list[Line]


@dataclass
class Run:
    """One execution of a real exercise by the project checker."""
    args: list[str] = field(default_factory=list)
    stdin: str = ""
    expect: list[str] = field(default_factory=list)
    expect_err: list[str] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)


@dataclass
class Exercise:
    """What the project checker verifies for one real exercise file."""
    folder: str
    filename: str
    brief: list[str]
    authorized: set[str]
    functions: list[str] = field(default_factory=list)
    classes: dict[str, str] = field(default_factory=dict)
    needs: list[str] = field(default_factory=list)
    forbid: list[str] = field(default_factory=list)
    runs: list[Run] = field(default_factory=list)


@dataclass
class World:
    id: str
    title: str
    project: str
    subtitle: str
    mentor: str
    intro: list[Line]
    chapters: list[Chapter]
    defense: list[Riddle]
    boss: Enemy
    exercises: list[Exercise]
    outro: list[Line]
