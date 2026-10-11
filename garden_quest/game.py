"""The main menu and the flow of each chapter."""

from pathlib import Path

from . import ui
from .battle import HeroFainted, Monster, Riddle, fight
from .chapters import (CHAPTERS, DEFENSE_RIDDLES, FINAL_STORY, MURPHY,
                       Chapter)
from .crystal_ball import run_snippet
from .final_trial import run_final_trial, show_briefing
from .forge import forge
from .hero import Hero, load, save

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FINAL = len(CHAPTERS)  # the final trial counts as chapter 5


def read_spellbook(chapter: Chapter) -> None:
    ui.title(f"📖 Grimoire - {chapter.title}")
    ui.say(f"  ({chapter.exercise})", "grey", slow=False)
    for number, page in enumerate(chapter.pages, start=1):
        print()
        ui.say(f"  ── Page {number}/{len(chapter.pages)} ──", "magenta",
               slow=False)
        for line in page.text:
            ui.say("  " + line)
        if page.code:
            ui.code_block(page.code)
        ui.pause()


def battle(hero: Hero, chapter_title: str, monster: Monster,
           riddles: list[Riddle]) -> None:
    """Fight until the monster falls. Fainting just restarts the fight."""
    while True:
        hero.heal()
        try:
            fight(hero, monster, riddles)
            return
        except HeroFainted as fainted:
            ui.say(f"\n  💤 {fainted}", "red")
            ui.say("  ...but a Guardian's program never crashes. The "
                   "Elder Gardener catches you", "cyan")
            ui.say("  (with an `except HeroFainted:` - look in "
                   "garden_quest/game.py!) and you get back up.", "cyan")
            ui.say("  Tip: re-read the Grimoire pages, then try again.",
                   "grey")
            if ui.ask("  Re-read the Grimoire first? (y/n) › ") == "y":
                for chapter in CHAPTERS:
                    if chapter.title == chapter_title:
                        read_spellbook(chapter)


def play_chapter(hero: Hero, chapter: Chapter) -> None:
    ui.title(f"Chapter {chapter.number}: {chapter.title}")
    ui.say(f"  {chapter.exercise}", "grey", slow=False)
    print()
    replay = 0
    if chapter.rune in hero.runes:
        replay = ui.choose("  You already beat this monster. › ",
                           ["Go straight to the Spell Forge",
                            "Replay the whole chapter"])
    if replay == 1 or chapter.rune not in hero.runes:
        ui.narrate(chapter.story)
        ui.pause()
        read_spellbook(chapter)
        battle(hero, chapter.title, chapter.monster, chapter.riddles)
        hero.learn(chapter.rune)
        ui.say(f"  You learned the {chapter.rune}!", "magenta")
        save(hero)
        ui.pause()
        ui.say("  The Elder Gardener nods. 'Knowing the spell is half of "
               "it.", "cyan")
        ui.say("  Now FORGE it with your own hands.'", "cyan")
    if forge(chapter.trial):
        if chapter.number not in hero.forges_done:
            hero.forges_done.append(chapter.number)
        if chapter.number not in hero.chapters_done:
            hero.chapters_done.append(chapter.number)
            hero.xp += 50
        print()
        ui.narrate(chapter.victory)
        ui.say(f"  ⭐ Chapter complete! Rank: {hero.rank}  XP: {hero.xp}",
               "green")
    else:
        ui.say("  The forge will wait for you. Choose this chapter again "
               "to continue.", "grey")
    save(hero)
    ui.pause()


def play_finale(hero: Hero) -> None:
    ui.title("Final Chapter: The Garden Guardian")
    ui.narrate(FINAL_STORY)
    ui.pause()
    battle(hero, "", MURPHY, DEFENSE_RIDDLES)
    hero.learn("👑 Crown of Understanding")
    save(hero)
    ui.pause()
    ui.say("  Now the real work. No disguises, no skeletons: YOUR project.",
           "cyan")
    show_briefing()
    print()
    ui.say("  Create the folders ex0/ .. ex4/ in your project repository,",
           slow=False)
    ui.say("  write each file yourself (your forge files are a great "
           "reference!),", slow=False)
    ui.say("  then let the Final Trial check them.", slow=False)
    while True:
        print()
        picked = ui.choose("  Final Trial › ", [
            "Check my project now",
            "Show the briefing again",
            "Back to the main menu",
        ])
        if picked == 0:
            answer = ui.ask(f"  Project folder [{Path.cwd()}] › ")
            root = Path(answer).expanduser() if answer else Path.cwd()
            if run_final_trial(root.resolve()):
                if FINAL not in hero.chapters_done:
                    hero.chapters_done.append(FINAL)
                save(hero)
                ending(hero)
                return
        elif picked == 1:
            show_briefing()
        else:
            return


def ending(hero: Hero) -> None:
    print()
    ui.title("🌻 THE GREENHOUSE THRIVES 🌻")
    ui.narrate([
        f"{hero.name}, the sensors still glitch. Drakes still wake.",
        "Files still go missing. Murphy will always be Murphy.",
        "But your programs bend instead of breaking. They catch, they",
        "raise, they name their problems, and they always clean up.",
        f"You are now: {hero.rank}.",
        "Go defend your project - and teach a peer what you learned.",
    ])


def crystal_ball_sandbox() -> None:
    ui.title("🔮 The Crystal Ball")
    ui.say("  Type any Python. Type `run` on its own line to cast it, "
           "`back` to leave.", slow=False)
    ui.say("  Try:  int('abc')   or   10 / 0   or a whole try/except!",
           "grey", slow=False)
    while True:
        lines: list[str] = []
        while True:
            line = ui.ask("  ... " if lines else "  >>> ", keep_indent=True)
            if line.strip() == "back" and not lines:
                return
            if line.strip() == "run":
                break
            lines.append(line)
        print(ui.paint(run_snippet("\n".join(lines)) or "(no output)",
                       "yellow"))


def hero_sheet(hero: Hero) -> None:
    ui.title(f"🧙 {hero.name} - {hero.rank}")
    print(f"  XP: {hero.xp}")
    print(f"  Chapters completed: {len(hero.chapters_done)}/{FINAL + 1}")
    print("  Runes:")
    for rune in hero.runes or ["(none yet)"]:
        print(f"     {rune}")
    ui.pause()


def chapter_label(hero: Hero, number: int, name: str) -> str:
    done = number in hero.chapters_done
    return f"{'✓' if done else ' '} {number}. {name}"


def main_menu(hero: Hero) -> None:
    while True:
        unlocked = len(hero.chapters_done)
        ui.title(f"🌿 Codehaven Greenhouse  -  {hero.name}, {hero.rank}")
        options = [chapter_label(hero, c.number, c.title)
                   for c in CHAPTERS[:unlocked + 1]]
        if unlocked >= len(CHAPTERS):
            options.append(chapter_label(hero, FINAL,
                                         "The Garden Guardian (finale)"))
        extras = ["📖 Read a Grimoire chapter", "🔮 Crystal Ball sandbox",
                  "⚖  Check my real project (ex0-ex4)", "🧙 Hero sheet",
                  "🚪 Save and quit"]
        picked = ui.choose("  Where to, Guardian? › ", options + extras)
        if picked < len(CHAPTERS) and picked < len(options):
            play_chapter(hero, CHAPTERS[picked])
            continue
        if picked < len(options):
            play_finale(hero)
            continue
        extra = picked - len(options)
        if extra == 0:
            index = ui.choose("  Which chapter? › ",
                              [c.title for c in CHAPTERS[:unlocked + 1]])
            read_spellbook(CHAPTERS[index])
        elif extra == 1:
            crystal_ball_sandbox()
        elif extra == 2:
            answer = ui.ask(f"  Project folder [{Path.cwd()}] › ")
            root = Path(answer).expanduser() if answer else Path.cwd()
            run_final_trial(root.resolve())
            ui.pause()
        elif extra == 3:
            hero_sheet(hero)
        else:
            return


def start() -> None:
    print(ui.paint(ui.BANNER, "green"))
    hero = load()
    if hero is None:
        ui.narrate([
            "Welcome, traveller. This is a game about Python exceptions:",
            "try, except, raise, custom errors and finally.",
            "Each chapter = one exercise of the Garden Guardian project.",
            "You'll read the Grimoire, battle with riddles, then FORGE",
            "real code in the workshop/ folder. At the end you write the",
            "real project yourself, and the game checks it.",
            "(Type `quit` at any prompt to save and leave.)",
        ])
        name = ui.ask("  What is your name, Guardian? › ") or "Guardian"
        hero = Hero(name=name)
        save(hero)
    else:
        ui.say(f"  Welcome back, {hero.name} the {hero.rank}!", "green")
    try:
        main_menu(hero)
    finally:
        save(hero)
        ui.say("\n  Your progress is saved. The greenhouse awaits your "
               "return. 🌱", "green", slow=False)
