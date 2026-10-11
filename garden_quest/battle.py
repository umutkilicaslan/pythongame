"""Riddle battles: answer correctly to hit the monster, mistakes hurt you.

Notice how this file uses the very spells the game teaches: when your
hero runs out of hearts, a HeroFainted exception is *raised*, and the
chapter that started the battle *catches* it and lets you try again.
"""

from dataclasses import dataclass

from . import ui
from .crystal_ball import run_snippet
from .hero import Hero


class HeroFainted(Exception):
    """Raised when the hero's hearts reach zero."""

    def __init__(self, message: str = "Your hero has fainted!") -> None:
        super().__init__(message)


@dataclass
class Riddle:
    """One question of a battle.

    kind "choice": the player picks one of `options`, `answer` is its index.
    kind "blank":  the player types a word, `answer` lists accepted words.
    If `run` is True, the Crystal Ball replays `code` after the answer.
    """
    question: str
    explain: str
    kind: str = "choice"
    code: str = ""
    options: tuple[str, ...] = ()
    answer: int | tuple[str, ...] = 0
    run: bool = False


@dataclass
class Monster:
    name: str
    art: str
    taunt: str
    defeat: str


def _is_correct(riddle: Riddle) -> bool:
    if riddle.kind == "choice":
        picked = ui.choose("  Your answer › ", list(riddle.options))
        return picked == riddle.answer
    typed = ui.ask("  Fill the blank › ").strip().lower()
    accepted = riddle.answer if isinstance(riddle.answer, tuple) else ()
    return typed in [word.lower() for word in accepted]


def _reveal(riddle: Riddle) -> None:
    if riddle.run and riddle.code:
        ui.say("  🔮 The Crystal Ball replays the spell with real Python:",
               "magenta", slow=False)
        for line in run_snippet(riddle.code).splitlines():
            print("     " + ui.paint(line, "grey"))
    ui.say("  📜 " + riddle.explain, "blue", slow=False)


def ask_riddle(riddle: Riddle) -> bool:
    print()
    ui.say("  " + riddle.question, "bold", slow=False)
    if riddle.code:
        ui.code_block(riddle.code)
    correct = _is_correct(riddle)
    if correct:
        ui.say("  ✨ Correct!", "green", slow=False)
    else:
        ui.say("  ✗ Not quite...", "red", slow=False)
    _reveal(riddle)
    return correct


def fight(hero: Hero, monster: Monster, riddles: list[Riddle]) -> None:
    """Run a battle. Raises HeroFainted if the hero loses all hearts.

    Every riddle you miss comes back later: the monster only falls when
    you have answered all of them correctly.
    """
    print(ui.paint(monster.art, "red"))
    ui.say(f"  {monster.name}: \"{monster.taunt}\"", "red")
    queue = list(riddles)
    monster_hp = len(riddles)
    while queue:
        print()
        print(f"  You {ui.bar(hero.hp, hero.max_hp, 'green')}    "
              f"{monster.name} {ui.bar(monster_hp, len(riddles), 'red', '■')}")
        riddle = queue.pop(0)
        if ask_riddle(riddle):
            monster_hp -= 1
            hero.xp += 10
            ui.say(f"  ⚔  Your spell hits {monster.name}!", "green")
        else:
            hero.hp -= 1
            queue.append(riddle)
            ui.say(f"  🩸 {monster.name} strikes back! (this riddle will "
                   "return)", "red")
            if hero.hp <= 0:
                raise HeroFainted()
        ui.pause()
    print()
    ui.say(f"  {monster.defeat}", "green")
