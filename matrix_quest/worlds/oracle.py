"""World 3 - The Oracle: Data Quest (Python collections).

Trials: transmissions instead of commands, pod energy instead of scores,
Zion coordinates, uploaded skills instead of achievements, the armory
instead of the inventory, the code rain instead of the event stream and
the Oracle's cookies instead of the alchemist's scores.
"""

import ast
import inspect

from ..forge import ForgeFailure, Spell, call, need, no_crash, script, uses
from ..model import (Chapter, Check, Enemy, Exercise, Line, Page, Riddle, Run,
                     Trial, World)
from . import art

ORACLE = "The Oracle"


def _run(spell: Spell, args: list[str], stdin: str = "") -> str:
    result = script(spell, args, stdin)
    no_crash(result, "`python3 " + " ".join([spell.path.name] + args) + "`")
    return result.stdout


def _expect(out: str, words: list[str], how: str) -> None:
    for word in words:
        if word not in out:
            raise ForgeFailure(f"{how}: the output should contain "
                               f"{word!r}")


# ============================================================ chapter 0

def _c0_none(spell: Spell) -> None:
    out = _run(spell, [])
    _expect(out, ["No messages", "Total arguments: 1"], "without arguments")


def _c0_some(spell: Spell) -> None:
    out = _run(spell, ["follow", "the", "rabbit"])
    _expect(out, ["Messages received: 3", "Message 1: follow",
                  "Message 3: rabbit", "Total arguments: 4"],
            "with 'follow the rabbit'")
    if "Message 0" in out or ".py" in out.split("Messages received")[-1]:
        raise ForgeFailure("don't list the program name as a message")


def _c0_quoted(spell: Spell) -> None:
    out = _run(spell, ["white rabbit"])
    _expect(out, ["Messages received: 1", "Message 1: white rabbit"],
            "with one quoted argument")


def _c0_argv(spell: Spell) -> None:
    if "sys.argv" not in spell.source:
        raise ForgeFailure("read the arguments from sys.argv")


TRIAL_0 = Trial(
    id="w3c0",
    filename="w3_0_transmission.py",
    mission=[
        "Messages from the real world arrive as command-line arguments.",
        "Show what you received:",
        "",
        "  $ python3 w3_0_transmission.py follow the rabbit",
        "  === Incoming Transmission ===",
        "  Program name: w3_0_transmission.py",
        "  Messages received: 3",
        "  Message 1: follow",
        "  Message 2: the",
        "  Message 3: rabbit",
        "  Total arguments: 4",
        "",
        "Without arguments, print 'No messages received!' instead of the",
        "messages. Use the Run button with arguments to try it!",
        "",
        "Subject: ex0/ft_command_quest.py.",
    ],
    skeleton='''import sys


if __name__ == "__main__":
    print("=== Incoming Transmission ===")
    # TODO: sys.argv is a list: [program name, argument 1, argument 2...]
''',
    hints=[
        "sys.argv[0] is the program's name; the real messages start at "
        "index 1. len(sys.argv) counts everything.",
        "A loop from 1: for i in range(1, len(sys.argv)): print(f'Message "
        "{i}: {sys.argv[i]}')",
        "Other ways to skip the name: slicing sys.argv[1:] - be ready to "
        "discuss both at evaluation.",
    ],
    checks=[
        ("no arguments: 'No messages', total 1", _c0_none),
        ("three arguments are listed and counted", _c0_some),
        ("a quoted argument stays one message", _c0_quoted),
        ("sys.argv is used", _c0_argv),
    ],
    run_args="follow the white rabbit",
)


# ============================================================ chapter 1

def _c1_stats(spell: Spell) -> None:
    out = _run(spell, ["120", "80", "100"])
    _expect(out, ["Readings: [120, 80, 100]", "Pods: 3", "Total: 300",
                  "Average: 100.0", "Max: 120", "Min: 80", "Range: 40"],
            "with 120 80 100")


def _c1_mixed(spell: Spell) -> None:
    out = _run(spell, ["12", "abc", "30"])
    _expect(out, ["Invalid reading: 'abc'", "Total: 42"],
            "with 12 abc 30 (abc is discarded)")


def _c1_empty(spell: Spell) -> None:
    out = _run(spell, [])
    _expect(out, ["Usage"], "without arguments")
    out = _run(spell, ["ab", "ac"])
    _expect(out, ["Invalid reading: 'ab'", "Invalid reading: 'ac'",
                  "Usage"], "with only invalid readings")


def _c1_try(spell: Spell) -> None:
    if not uses(spell, ast.Try):
        raise ForgeFailure("convert with int() inside a try/except")


TRIAL_1 = Trial(
    id="w3c1",
    filename="w3_1_pods.py",
    mission=[
        "Tank reads the energy of each pod from the command line.",
        "Store the valid readings in a NEW list and show the stats:",
        "",
        "  $ python3 w3_1_pods.py 120 80 100",
        "  === Pod Energy Analytics ===",
        "  Readings: [120, 80, 100]",
        "  Pods: 3",
        "  Total: 300",
        "  Average: 100.0",
        "  Max: 120",
        "  Min: 80",
        "  Range: 40",
        "",
        "Non-numbers: print  Invalid reading: 'abc'  and discard them.",
        "No valid reading at all:",
        "  No readings. Usage: python3 w3_1_pods.py <reading1> ...",
        "",
        "Subject: ex1/ft_score_analytics.py.",
    ],
    skeleton='''import sys


if __name__ == "__main__":
    print("=== Pod Energy Analytics ===")
    readings: list[int] = []
    # TODO: convert each argument, keep the valid ones in readings
    # TODO: the stats (len, sum, max, min) - or the usage message
''',
    hints=[
        "readings.append(int(arg)) inside a try; except ValueError: print "
        "the invalid one.",
        "len(), sum(), max(), min() all work on a list. Average = sum / "
        "len (a float).",
        "Check `if not readings:` (or len(readings) == 0) before computing:"
        " max([]) crashes!",
    ],
    checks=[
        ("stats for 120 80 100", _c1_stats),
        ("invalid readings are discarded", _c1_mixed),
        ("no valid reading prints the usage", _c1_empty),
        ("try/except protects the conversion", _c1_try),
    ],
    run_args="120 80 100 abc",
)


# ============================================================ chapter 2

def _coords(spell: Spell, stdin: str) -> tuple[object, str]:
    result = call(need(spell, "get_coords"), stdin=stdin)
    if isinstance(result.error, EOFError):
        raise ForgeFailure(f"with input {stdin!r}, get_coords() kept asking"
                           " after a valid answer")
    if result.error is not None:
        raise ForgeFailure(f"get_coords() crashed: {result.error!r}")
    return result.value, result.output


def _c2_valid(spell: Spell) -> None:
    value, _ = _coords(spell, "1,2,2\n")
    if not isinstance(value, tuple) or value != (1.0, 2.0, 2.0):
        raise ForgeFailure(f"typing 1,2,2 should return the tuple "
                           f"(1.0, 2.0, 2.0), got {value!r}")


def _c2_syntax(spell: Spell) -> None:
    value, out = _coords(spell, "hello world\n1 , 2.5, 3\n")
    if value != (1.0, 2.5, 3.0):
        raise ForgeFailure(f"after a bad line, retry: '1 , 2.5, 3' should "
                           f"give (1.0, 2.5, 3.0), got {value!r}")
    if "Invalid" not in out:
        raise ForgeFailure("print 'Invalid syntax' for 'hello world'")


def _c2_number(spell: Spell) -> None:
    value, out = _coords(spell, "4,abc,5\n4,5,6\n")
    if value != (4.0, 5.0, 6.0):
        raise ForgeFailure(f"expected (4.0, 5.0, 6.0) after the retry, got"
                           f" {value!r}")
    if "abc" not in out:
        raise ForgeFailure("name the bad parameter: Error on parameter "
                           "'abc': ...")


def _c2_distances(spell: Spell) -> None:
    out = _run(spell, [], "1,2,2\n4,6,2\n")
    _expect(out, ["(1.0, 2.0, 2.0)", "3.0", "5.0"],
            "with (1,2,2) then (4,6,2)")


TRIAL_2 = Trial(
    id="w3c2",
    filename="w3_2_coordinates.py",
    mission=[
        "Zion's position must be written in stone: tuples.",
        "",
        "  get_coords() -> tuple[float, float, float]",
        "      asks  Enter coordinates as 'x,y,z':  with input()",
        "      wrong number of parts -> print 'Invalid syntax', ask again",
        "      a part isn't a float -> print",
        "          Error on parameter 'abc': <the error>   and ask again",
        "      returns the tuple once it's valid",
        "",
        "Main guard: get a first position, print the tuple and each of",
        "X, Y, Z, the distance to (0, 0, 0); then a second position and",
        "the distance between both - with math.sqrt and round(.., 4).",
        "",
        "Subject: ex2/ft_coordinate_system.py (get_player_pos).",
    ],
    skeleton='''import math


def get_coords() -> tuple[float, float, float]:
    while True:
        text = input("Enter coordinates as 'x,y,z': ")
        parts = text.split(",")
        # TODO: 3 parts? each one a float? -> return a tuple


if __name__ == "__main__":
    print("=== Zion Coordinate System ===")
    # TODO
''',
    hints=[
        "text.split(',') gives a list of strings. len(parts) != 3 means "
        "invalid syntax.",
        "float(' 2.5 ') works, spaces included. Convert one part at a time "
        "inside a try to know WHICH one failed.",
        "Distance: math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) "
        "** 2). A tuple unpacks: x, y, z = position.",
    ],
    checks=[
        ("'1,2,2' returns (1.0, 2.0, 2.0)", _c2_valid),
        ("bad syntax is reported and retried", _c2_syntax),
        ("a bad number is named and retried", _c2_number),
        ("the distances are right", _c2_distances),
    ],
    run_stdin="1,2,2\n4,6,2\n",
)


# ============================================================ chapter 3

CREW = {"Neo": {"Kung Fu", "Jiu Jitsu", "Flying"},
        "Trinity": {"Kung Fu", "Helicopter Pilot", "Motorbike"},
        "Morpheus": {"Kung Fu", "Jiu Jitsu", "Leadership"}}


def _c3_gen(spell: Spell) -> None:
    skills = need(spell, "SKILLS")
    results = [call(need(spell, "gen_skills")) for _ in range(30)]
    for result in results:
        if result.error is not None:
            raise ForgeFailure(f"gen_skills() crashed: {result.error!r}")
        if not isinstance(result.value, set):
            raise ForgeFailure(f"gen_skills() should return a set, got "
                               f"{type(result.value).__name__}")
        if not result.value <= set(skills):
            raise ForgeFailure("gen_skills() returned skills that are not "
                               "in SKILLS")
    if len({frozenset(result.value) for result in results}) < 2:
        raise ForgeFailure("gen_skills() always returns the same set: use "
                           "random")


def _c3_fn(name: str, expected: set[str], *extra: str) -> Check:
    def check(spell: Spell) -> None:
        result = call(need(spell, name), CREW, *extra)
        if result.error is not None:
            raise ForgeFailure(f"{name}() crashed: {result.error!r}")
        if result.value != expected:
            raise ForgeFailure(f"{name}(crew{', ' if extra else ''}"
                               f"{', '.join(map(repr, extra))}) should be "
                               f"{expected}, got {result.value!r}")
    return check


def _c3_missing(spell: Spell) -> None:
    skills = set(need(spell, "SKILLS"))
    result = call(need(spell, "missing"), CREW, "Neo")
    expected = skills - CREW["Neo"]
    if result.value != expected:
        raise ForgeFailure("missing(crew, 'Neo') should be every skill in "
                           "SKILLS that Neo doesn't have")


def _c3_main(spell: Spell) -> None:
    _run(spell, [])


TRIAL_3 = Trial(
    id="w3c3",
    filename="w3_3_skills.py",
    mission=[
        "\"I know Kung Fu.\" Skills are uploaded at random into the crew.",
        "Each skill counts once: sets.",
        "",
        "  SKILLS: list[str]   a long fixed list (keep the one given)",
        "  gen_skills() -> set[str]",
        "      picks a random number of skills from SKILLS",
        "  all_skills(crew: dict[str, set[str]]) -> set[str]   union",
        "  common_skills(crew) -> set[str]       shared by EVERYONE",
        "  only_has(crew, name) -> set[str]      nobody else has them",
        "  missing(crew, name) -> set[str]       SKILLS they don't have",
        "",
        "Main guard: 4 crew members (Neo, Trinity, Morpheus, Tank) and",
        "print all the results.",
        "",
        "Subject: ex3/ft_achievement_tracker.py.",
    ],
    skeleton='''import random

SKILLS = ["Kung Fu", "Jiu Jitsu", "Drunken Boxing", "Helicopter Pilot",
          "Motorbike", "Flying", "Bullet Dodging", "Wall Running",
          "Leadership", "Lock Picking", "Hacking", "Spoon Bending"]


def gen_skills() -> set[str]:
    # TODO: a random number of skills, picked from SKILLS
    return set()


def all_skills(crew: dict[str, set[str]]) -> set[str]:
    return set()  # TODO


def common_skills(crew: dict[str, set[str]]) -> set[str]:
    return set()  # TODO


def only_has(crew: dict[str, set[str]], name: str) -> set[str]:
    return set()  # TODO


def missing(crew: dict[str, set[str]], name: str) -> set[str]:
    return set()  # TODO


if __name__ == "__main__":
    print("=== Skill Upload Tracker ===")
    crew = {name: gen_skills() for name in
            ["Neo", "Trinity", "Morpheus", "Tank"]}
''',
    hints=[
        "random.randint(a, b) picks a number, random.sample(SKILLS, n) "
        "picks n different skills. set(...) turns the list into a set.",
        "a.union(b), a.intersection(b), a.difference(b) - or | & -. Start "
        "from an empty set() and union everyone in a loop.",
        "only_has: the member's skills minus the union of everybody ELSE. "
        "An empty set prints as set(), not {} - why? ({} is a dict!)",
    ],
    checks=[
        ("gen_skills() returns random sets from SKILLS", _c3_gen),
        ("all_skills() is the union",
         _c3_fn("all_skills", {"Kung Fu", "Jiu Jitsu", "Flying",
                               "Helicopter Pilot", "Motorbike",
                               "Leadership"})),
        ("common_skills() is the intersection",
         _c3_fn("common_skills", {"Kung Fu"})),
        ("only_has() finds unique skills",
         _c3_fn("only_has", {"Helicopter Pilot", "Motorbike"}, "Trinity")),
        ("missing() lists what's left", _c3_missing),
        ("the main program runs", _c3_main),
    ],
)


# ============================================================ chapter 4

def _c4_parse(spell: Spell) -> None:
    args = ["guns:5", "guns:2", "hello", "ammo:x", "coats:1"]
    result = call(need(spell, "parse_armory"), args)
    if result.error is not None:
        raise ForgeFailure(f"parse_armory crashed: {result.error!r}")
    if result.value != {"guns": 5, "coats": 1}:
        raise ForgeFailure(f"parse_armory({args}) should give "
                           f"{{'guns': 5, 'coats': 1}}, got {result.value!r}")
    for word in ("guns", "hello", "ammo"):
        if word not in result.output:
            raise ForgeFailure(f"print an error message about {word!r}")


def _c4_report(spell: Spell) -> None:
    out = _run(spell, ["guns:5", "coats:1", "ammo:6"])
    _expect(out, ["Total quantity: 12", "50.0%", "Most abundant: ammo",
                  "Least abundant: coats", "Updated armory"],
            "with guns:5 coats:1 ammo:6")


def _c4_tie(spell: Spell) -> None:
    out = _run(spell, ["lasers:2", "boots:2"])
    _expect(out, ["Most abundant: lasers", "Least abundant: lasers"],
            "in a tie, choose the first from the command line")


TRIAL_4 = Trial(
    id="w3c4",
    filename="w3_4_armory.py",
    mission=[
        "\"What do you need?\" - \"Guns. Lots of guns.\"",
        "Fill the armory (a dict) from arguments like  guns:5",
        "",
        "  parse_armory(args: list[str]) -> dict[str, int]",
        "      bad syntax  -> Error - invalid parameter 'hello'",
        "      bad number  -> Quantity error for 'ammo': <error>",
        "      seen before -> Redundant item 'guns' - discarding",
        "",
        "Main guard, with the parsed armory:",
        "  Armory: {...}            Items: [...]",
        "  Total quantity: 12",
        "  Item guns represents 41.7%       (one line per item)",
        "  Most abundant: ammo with quantity 6",
        "  Least abundant: coats with quantity 1   (ties: first one)",
        "  then add 'keys': 1 and print  Updated armory: {...}",
        "",
        "Subject: ex4/ft_inventory_system.py.",
    ],
    skeleton='''import sys


def parse_armory(args: list[str]) -> dict[str, int]:
    armory: dict[str, int] = {}
    for arg in args:
        pass  # TODO
    return armory


if __name__ == "__main__":
    print("=== The Armory ===")
    armory = parse_armory(sys.argv[1:])
    # TODO
''',
    hints=[
        "arg.split(':') must give exactly 2 parts. `name in armory` tells "
        "if it's redundant.",
        "list(armory.keys()), sum(armory.values()). Percent: round(qty / "
        "total * 100, 1).",
        "For the most abundant, loop and keep the best so far, replacing "
        "it only when STRICTLY bigger - that keeps the first in a tie. "
        "armory.update({'keys': 1}) adds an item.",
    ],
    checks=[
        ("parse_armory() keeps only valid, new items", _c4_parse),
        ("the full report is right", _c4_report),
        ("ties go to the first item", _c4_tie),
    ],
    run_args="guns:5 coats:1 ammo:6 guns:2 hello",
)


# ============================================================ chapter 5

def _c5_endless(spell: Spell) -> None:
    gen = need(spell, "gen_events")
    if not inspect.isgeneratorfunction(gen):
        raise ForgeFailure("gen_events must be a generator function (yield)")
    stream = gen()
    events = [next(stream) for _ in range(300)]
    for event in events:
        if not (isinstance(event, tuple) and len(event) == 2 and
                all(isinstance(part, str) for part in event)):
            raise ForgeFailure(f"each event is a (name, action) tuple, got "
                               f"{event!r}")
    if len(set(events)) < 3:
        raise ForgeFailure("the events should be random")


def _c5_consume(spell: Spell) -> None:
    consume = need(spell, "consume")
    if not inspect.isgeneratorfunction(consume):
        raise ForgeFailure("consume must be a generator function (yield)")
    events = [("Neo", "dodge"), ("Trinity", "fly"), ("Tank", "load"),
              ("Neo", "jump"), ("Morpheus", "fight")]
    backup = list(events)
    got = list(consume(events))
    if sorted(got) != sorted(backup):
        raise ForgeFailure(f"consume should yield every event once, got "
                           f"{got}")
    if events:
        raise ForgeFailure("each yielded event must be REMOVED from the "
                           "list: it should be empty at the end")


def _c5_main(spell: Spell) -> None:
    out = _run(spell, [])
    _expect(out, ["Event 999"], "the main program")


TRIAL_5 = Trial(
    id="w3c5",
    filename="w3_5_rain.py",
    mission=[
        "The code rain never ends. Don't store it: generate it.",
        "",
        "  gen_events()  endless generator, yields (name, action) tuples",
        "      with a random crew member and a random action",
        "  consume(events: list[tuple[str, str]])  generator that picks a",
        "      random element, REMOVES it from the list and yields it,",
        "      until the list is empty",
        "",
        "Main guard: print 1000 events  'Event 0: Neo did dodge' ...",
        "build a list of 10 events with next(), then",
        "  for event in consume(events): ... print it and what remains",
        "",
        "Subject: ex5/ft_data_stream.py (gen_event, consume_event).",
    ],
    skeleton='''import random
import typing

CREW = ["Neo", "Trinity", "Morpheus", "Tank"]
ACTIONS = ["dodge", "jump", "fight", "fly", "load", "hack"]


def gen_events() -> typing.Generator[tuple[str, str], None, None]:
    while True:
        pass  # TODO: yield one random event


def consume(events: list[tuple[str, str]]
            ) -> typing.Generator[tuple[str, str], None, None]:
    pass  # TODO


if __name__ == "__main__":
    print("=== Digital Rain ===")
    stream = gen_events()
    # TODO
''',
    hints=[
        "yield hands ONE value back and pauses the function, right there, "
        "until the next next().",
        "random.choice(CREW) picks one element. In consume: while events: "
        "pick with random.choice, events.remove(it), yield it.",
        "for i in range(1000): name, action = next(stream) - tuples unpack.",
    ],
    checks=[
        ("gen_events() is an endless random generator", _c5_endless),
        ("consume() empties the list one by one", _c5_consume),
        ("the main program shows 1000 events", _c5_main),
    ],
)


# ============================================================ chapter 6

NAMES = ["Neo", "trinity", "Morpheus", "tank", "Niobe", "link"]


def _comprehension(spell: Spell, function: str, kind: type) -> None:
    for node in ast.walk(spell.tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            if any(isinstance(child, kind) for child in ast.walk(node)):
                return
            raise ForgeFailure(f"{function}() must use a "
                               f"{'list' if kind is ast.ListComp else 'dict'}"
                               " comprehension")
    raise ForgeFailure(f"{function}() is missing")


def _c6_capitalize(spell: Spell) -> None:
    _comprehension(spell, "capitalize_all", ast.ListComp)
    got = call(need(spell, "capitalize_all"), NAMES).value
    if got != [name.capitalize() for name in NAMES]:
        raise ForgeFailure(f"capitalize_all gave {got!r}")


def _c6_only(spell: Spell) -> None:
    _comprehension(spell, "only_capitalized", ast.ListComp)
    got = call(need(spell, "only_capitalized"), NAMES).value
    if got != ["Neo", "Morpheus", "Niobe"]:
        raise ForgeFailure(f"only_capitalized gave {got!r}")


def _c6_scores(spell: Spell) -> None:
    _comprehension(spell, "score_board", ast.DictComp)
    got = call(need(spell, "score_board"), ["Neo", "Tank"]).value
    if not isinstance(got, dict) or set(got) != {"Neo", "Tank"} or \
            not all(isinstance(v, int) for v in got.values()):
        raise ForgeFailure(f"score_board(['Neo', 'Tank']) should map each "
                           f"name to a random int, got {got!r}")


def _c6_above(spell: Spell) -> None:
    _comprehension(spell, "above_average", ast.DictComp)
    scores = {"Neo": 900, "Tank": 100, "Link": 500, "Niobe": 600}
    got = call(need(spell, "above_average"), scores).value
    if got != {"Neo": 900, "Niobe": 600}:
        raise ForgeFailure(f"the average is 525: expected {{'Neo': 900, "
                           f"'Niobe': 600}}, got {got!r}")


TRIAL_6 = Trial(
    id="w3c6",
    filename="w3_6_cookies.py",
    mission=[
        "\"Here, take a cookie.\" The Oracle wants condensed, elegant code:",
        "each function holds ONE comprehension (on one line if it fits).",
        "",
        "  capitalize_all(names: list[str]) -> list[str]",
        "  only_capitalized(names: list[str]) -> list[str]",
        "      keeps only the names that were already capitalized",
        "  score_board(names: list[str]) -> dict[str, int]",
        "      each name -> a random score between 0 and 1000",
        "  above_average(scores: dict[str, int]) -> dict[str, int]",
        "      only the scores strictly above the average",
        "",
        "Main guard: show the lists and dicts for a crew of names.",
        "",
        "Subject: ex6/ft_data_alchemist.py.",
    ],
    skeleton='''import random


def capitalize_all(names: list[str]) -> list[str]:
    return []  # TODO: [... for name in names]


def only_capitalized(names: list[str]) -> list[str]:
    return []  # TODO


def score_board(names: list[str]) -> dict[str, int]:
    return {}  # TODO: {...: ... for name in names}


def above_average(scores: dict[str, int]) -> dict[str, int]:
    return {}  # TODO


if __name__ == "__main__":
    print("=== The Oracle's Cookies ===")
    crew = ["Neo", "trinity", "Morpheus", "tank", "Niobe", "link"]
''',
    hints=[
        "[name.capitalize() for name in names] - a loop that builds a list,"
        " in one line.",
        "Add a filter at the end: [... for name in names if name == "
        "name.capitalize()]",
        "{name: random.randint(0, 1000) for name in names}. For "
        "above_average, compute average = sum(scores.values()) / "
        "len(scores) first, then filter with .items().",
    ],
    checks=[
        ("capitalize_all() uses a list comprehension", _c6_capitalize),
        ("only_capitalized() filters", _c6_only),
        ("score_board() builds a dict comprehension", _c6_scores),
        ("above_average() keeps the high scores", _c6_above),
    ],
)


# ============================================================ the story

CHAPTERS = [
    Chapter(
        id="w3c0",
        title="Messages From the Outside",
        exercise="ex0 · ft_command_quest.py",
        concept="lists · sys.argv · indexes",
        story=[
            Line(ORACLE, "I'd ask you to sit down, but you're not going to"
                 " anyway."),
            Line(ORACLE, "Everything that comes into a program arrives "
                 "somehow. The first door is the command line."),
            Line("Tank", "When you type  python3 file.py a b c , Python "
                 "hands you a list: sys.argv."),
        ],
        pages=[
            Page("A list you already have", [
                "import sys gives you sys.argv: a list of strings, like "
                "argv in C. Index 0 is the program name, then each "
                "argument.",
                "len(list) counts the elements; list[i] reads one (from "
                "0); list[1:] is a slice: everything from index 1.",
            ], 'import sys\n\n'
               'print(sys.argv)\n'
               'print("Arguments:", len(sys.argv) - 1)'),
            Page("Looping over arguments", [
                "Quotes on the command line group words: \"white rabbit\" "
                "is ONE argument. Every argument is a str, even 42.",
            ], 'import sys\n\n'
               'for i in range(1, len(sys.argv)):\n'
               '    print(f"Argument {i}: {sys.argv[i]}")'),
        ],
        enemy=Enemy("the Line Tracer", art.SENTINEL,
                    "*beep* *beep* ...tracing the call...",
                    "Every message read, the trace lost."),
        riddles=[
            Riddle("You run  python3 quest.py hello 42 .  What is "
                   "len(sys.argv)?",
                   options=("2", "3", "1"), answer=1,
                   explain="['quest.py', 'hello', '42']: the name counts."),
            Riddle("What does this print?",
                   code='items = ["quest.py", "hello", "42"]\n'
                        'print(items[1:])',
                   options=("['hello', '42']", "['quest.py']",
                            "['quest.py', 'hello']"),
                   answer=0, run=True,
                   explain="A slice from index 1 to the end."),
            Riddle("What does this print?", run=True,
                   code='args = ["quest.py", "hello", "42"]\n'
                        'print(type(args[2]).__name__)',
                   options=("int", "str"), answer=1,
                   explain="Arguments are ALWAYS strings."),
            Riddle("What does this print?", run=True,
                   code='crew = ["Neo", "Trinity"]\nprint(crew[2])',
                   options=("None", "It crashes: IndexError"),
                   answer=1, explain="Index 2 doesn't exist (0 and 1 do)."),
        ],
        trial=TRIAL_0,
        victory=[Line(ORACLE, "You read what you were given. That's a "
                      "start.")],
    ),
    Chapter(
        id="w3c1",
        title="Pod Energy",
        exercise="ex1 · ft_score_analytics.py",
        concept="building lists · sum/min/max · try/except",
        story=[
            Line("Morpheus", "What is real? Electrical signals. The "
                 "machines farm us for energy, pod by pod."),
            Line("Tank", "I've got the energy readings of a field of pods "
                 "here. Some are garbage. Can you crunch them?"),
        ],
        pages=[
            Page("Building a list", [
                "Start with an empty list and .append() what you keep. "
                "Lists are ordered, indexed and expandable.",
            ], 'readings: list[int] = []\n'
               'for text in ["120", "abc", "80"]:\n'
               '    try:\n'
               '        readings.append(int(text))\n'
               '    except ValueError:\n'
               '        print(f"Invalid reading: {text!r}")\n'
               'print(readings)'),
            Page("Stats in one call each", [
                "len(), sum(), max() and min() work on any list of "
                "numbers. But max([]) crashes: check for an empty list "
                "first!",
            ], 'readings = [120, 80, 100]\n'
               'print(sum(readings) / len(readings))\n'
               'print(max(readings) - min(readings))'),
        ],
        enemy=Enemy("the Power Plant", art.SENTINEL,
                    "Human... battery... level... nominal...",
                    "The garbage readings are filtered. Tank cheers."),
        riddles=[
            Riddle("What does this print?", run=True,
                   code='scores = [1500, 2300, 1800]\n'
                        'scores.append(900)\nprint(len(scores), '
                        'max(scores), min(scores))',
                   options=("4 2300 900", "3 2300 1500", "4 900 2300"),
                   answer=0, explain="append adds at the end."),
            Riddle("What does this print?", run=True,
                   code='print(sum([10, 20]) / len([10, 20]))',
                   options=("15", "15.0"), answer=1,
                   explain="/ always gives a float in Python 3."),
            Riddle("What happens here?", run=True,
                   code='print(max([]))',
                   options=("It prints 0", "It crashes: ValueError, "
                            "empty sequence"), answer=1,
                   explain="That's why you check for 'no valid input' "
                           "first."),
            Riddle("{text!r} inside an f-string shows...",
                   code='text = "abc"\nprint(f"Invalid: {text!r}")',
                   options=("Invalid: abc", "Invalid: 'abc'"), answer=1,
                   run=True, explain="!r uses repr(): quotes included."),
        ],
        trial=TRIAL_1,
        victory=[Line("Tank", "Clean data! Look at those averages.")],
    ),
    Chapter(
        id="w3c2",
        title="The Coordinates of Zion",
        exercise="ex2 · ft_coordinate_system.py",
        concept="tuples · input() · retry loops · math.sqrt",
        story=[
            Line("Morpheus", "Zion. The last human city, near the earth's "
                 "core, where it's still warm."),
            Line("Niobe", "Its coordinates never change. They must be "
                 "written in stone."),
            Line(ORACLE, "In Python, stone is called a tuple."),
        ],
        pages=[
            Page("Tuples", [
                "A tuple is an ordered collection that can't change "
                "(immutable). Perfect for coordinates.",
                "Unpacking gives each part a name.",
            ], 'zion = (1.0, 2.5, 3.0)\n'
               'x, y, z = zion\n'
               'print(zion, x, y, z)'),
            Page("Asking until it's right", [
                "input() returns what the user typed, as a str. A "
                "while True loop asks again and again; return leaves it "
                "once the answer is valid.",
            ], 'def ask_number() -> float:\n'
               '    while True:\n'
               '        text = input("Number: ")\n'
               '        try:\n'
               '            return float(text)\n'
               '        except ValueError as e:\n'
               '            print("Error:", e)'),
            Page("Distance in 3D", [
                "import math gives math.sqrt(). The 3D Pythagorean "
                "theorem: sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2).",
            ], 'import math\n\nprint(round(math.sqrt(3 ** 2 + 4 ** 2), 4))'),
        ],
        enemy=Enemy("the Sentinel Squad", art.SENTINEL,
                    "*They scan every coordinate for Zion*",
                    "The coordinates stay locked in their tuple. Zion is "
                    "safe."),
        riddles=[
            Riddle("What happens here?", run=True,
                   code='zion = (1.0, 2.0, 3.0)\nzion[0] = 5.0',
                   options=("zion becomes (5.0, 2.0, 3.0)",
                            "It crashes: tuples can't be changed"),
                   answer=1, explain="Tuples are immutable."),
            Riddle("What does this print?", run=True,
                   code='print("1,2.5,3".split(","))',
                   options=("['1', '2.5', '3']", "[1, 2.5, 3]",
                            "('1', '2.5', '3')"),
                   answer=0, explain="split gives a list of STRINGS."),
            Riddle("What does this print?", run=True,
                   code='print(float(" 2.5 "))',
                   options=("2.5", "It crashes"), answer=0,
                   explain="float() ignores surrounding spaces."),
            Riddle("What does this print?", run=True,
                   code='import math\n\n'
                        'print(math.sqrt(1 ** 2 + 2 ** 2 + 2 ** 2))',
                   options=("3.0", "5.0", "9.0"), answer=0,
                   explain="sqrt(1 + 4 + 4) = sqrt(9) = 3."),
        ],
        trial=TRIAL_2,
        victory=[Line("Niobe", "Coordinates locked. Nobody moves Zion.")],
    ),
    Chapter(
        id="w3c3",
        title="I Know Kung Fu",
        exercise="ex3 · ft_achievement_tracker.py",
        concept="sets · union · intersection · difference",
        story=[
            Line("Tank", "Uploading combat training..."),
            Line("Neo", "...I know Kung Fu."),
            Line("Morpheus", "Show me."),
            Line(ORACLE, "Each skill counts once, no matter how many times "
                 "you upload it. That's a set."),
        ],
        pages=[
            Page("Sets", [
                "A set holds UNIQUE elements, with no order. Adding a "
                "duplicate does nothing. Checking 'x in my_set' is "
                "lightning fast - that's why big systems use them.",
            ], 'skills = {"Kung Fu", "Jiu Jitsu", "Kung Fu"}\n'
               'print(len(skills))\n'
               'print(set())     # the empty set ({} is a dict!)'),
            Page("Set algebra", [
                "union: in either. intersection: in both. difference: in "
                "the first but not the second.",
            ], 'neo = {"Kung Fu", "Flying"}\n'
               'trinity = {"Kung Fu", "Motorbike"}\n'
               'print(neo.union(trinity))\n'
               'print(neo.intersection(trinity))\n'
               'print(neo.difference(trinity))'),
        ],
        enemy=Enemy("Morpheus (sparring)", art.AGENT,
                    "What are you waiting for? You're faster than this.",
                    "Morpheus bows. \"Your skills are unique, Neo.\""),
        riddles=[
            Riddle("What does this print?", run=True,
                   code='print(len({"Kung Fu", "Kung Fu", "Flying"}))',
                   options=("3", "2"), answer=1,
                   explain="Duplicates disappear in a set."),
            Riddle("What does this print?", run=True,
                   code='a = {"Kung Fu", "Flying"}\n'
                        'b = {"Kung Fu", "Motorbike"}\n'
                        'print(a.intersection(b))',
                   options=("{'Kung Fu'}", "{'Flying', 'Motorbike'}",
                            "set()"),
                   answer=0, explain="Only what both have."),
            Riddle("What does this print?", run=True,
                   code='a = {"Kung Fu"}\nb = {"Kung Fu"}\n'
                        'print(a.difference(b))',
                   options=("{}", "set()", "None"), answer=1,
                   explain="An empty SET prints as set(); {} would be an "
                           "empty dict."),
            Riddle("Why is 'x in a_set' faster than 'x in a_list' for big "
                   "collections?",
                   options=("It isn't",
                            "Sets use hashing: they jump straight to the "
                            "element instead of checking one by one"),
                   answer=1, explain="That's the Twitter story in the "
                                     "subject's foreword."),
        ],
        trial=TRIAL_3,
        victory=[Line("Morpheus", "Unique, shared, missing... you see the "
                      "whole crew now.")],
    ),
    Chapter(
        id="w3c4",
        title="The Armory",
        exercise="ex4 · ft_inventory_system.py",
        concept="dicts · keys/values · update",
        story=[
            Line("Tank", "So what do you need? Besides a miracle."),
            Line("Neo", "Guns. Lots of guns."),
            Line(ORACLE, "Every item has a name and a quantity. A name that"
                 " opens a value: a dictionary."),
        ],
        pages=[
            Page("Dictionaries", [
                "A dict maps keys to values: armory['guns'] = 5. Keys are "
                "unique; 'key in d' checks if one exists.",
            ], 'armory = {"guns": 5, "coats": 1}\n'
               'armory["ammo"] = 300\n'
               'print(armory)\n'
               'print("guns" in armory)'),
            Page("Looking inside", [
                "keys(), values(), items() let you loop. update() merges "
                "another dict in. Since Python 3.7, dicts keep insertion "
                "order.",
            ], 'armory = {"guns": 5, "coats": 1}\n'
               'print(list(armory.keys()), sum(armory.values()))\n'
               'for name, qty in armory.items():\n'
               '    print(name, qty)\n'
               'armory.update({"keys": 1})\n'
               'print(armory)'),
        ],
        enemy=Enemy("the Lobby Guards", art.CROWD,
                    "*metal detector beeps*",
                    "The armory is sorted. The lobby scene goes better than"
                    " planned."),
        riddles=[
            Riddle("What does this print?", run=True,
                   code='d = {"guns": 5}\nd["guns"] = 7\nprint(d)',
                   options=("{'guns': 7}", "{'guns': 5, 'guns': 7}"),
                   answer=0, explain="A key exists once: it's replaced."),
            Riddle("What happens here?", run=True,
                   code='d = {"guns": 5}\nprint(d["swords"])',
                   options=("None", "It crashes: KeyError 'swords'"),
                   answer=1, explain="Check with 'in' first."),
            Riddle("What does this print?", run=True,
                   code='print("guns:5".split(":"))',
                   options=("['guns', '5']", "['guns', 5]",
                            "('guns', '5')"), answer=0,
                   explain="Two strings; int() the second one."),
            Riddle("What does this print?", run=True,
                   code='print(round(5 / 12 * 100, 1))',
                   options=("41.7", "41.6", "42"), answer=0,
                   explain="That's how you get the percentage."),
        ],
        trial=TRIAL_4,
        victory=[Line("Trinity", "Lots of guns. Sorted by name.")],
    ),
    Chapter(
        id="w3c5",
        title="The Digital Rain",
        exercise="ex5 · ft_data_stream.py",
        concept="generators · yield · next()",
        story=[
            Line("Cypher", "I don't even see the code anymore. All I see "
                 "is blonde, brunette, redhead..."),
            Line(ORACLE, "The rain never ends. If you tried to store it "
                 "all, you'd need infinite memory."),
            Line(ORACLE, "So don't store it. Produce it drop by drop: a "
                 "generator."),
        ],
        pages=[
            Page("yield", [
                "A function containing yield is a generator. Calling it "
                "runs nothing yet: it returns a generator object. Each "
                "next() runs until the next yield, hands the value over, "
                "and pauses there.",
            ], 'import typing\n\n\n'
               'def countdown() -> typing.Generator[int, None, None]:\n'
               '    yield 3\n'
               '    yield 2\n'
               '    yield 1\n'
               '\n'
               '\n'
               'gen = countdown()\n'
               'print(next(gen), next(gen))'),
            Page("Endless streams and for loops", [
                "A while True with a yield inside never runs out, and "
                "costs no memory. A for loop calls next() for you until "
                "the generator stops.",
            ], 'import typing\n\n\n'
               'def numbers() -> typing.Generator[int, None, None]:\n'
               '    n = 0\n'
               '    while True:\n'
               '        yield n\n'
               '        n += 1\n'
               '\n'
               '\n'
               'stream = numbers()\n'
               'print([next(stream) for _ in range(5)])'),
        ],
        enemy=Enemy("the Trainman", art.DAEMON,
                    "Down here, I'm God. And my trains never stop.",
                    "Event after event, on demand. The Trainman's station "
                    "goes quiet."),
        riddles=[
            Riddle("What does this print?", run=True,
                   code='def gen():\n    print("start")\n    yield 1\n\n\n'
                        'g = gen()\nprint("created")\nprint(next(g))',
                   options=("start / created / 1", "created / start / 1"),
                   answer=1,
                   explain="Calling gen() runs nothing until next()."),
            Riddle("What happens here?", run=True,
                   code='def gen():\n    yield 1\n\n\n'
                        'g = gen()\nprint(next(g))\nprint(next(g))',
                   options=("1 / 1", "1, then a crash: StopIteration"),
                   answer=1, explain="Once a generator is done, next() "
                                     "raises StopIteration."),
            Riddle("What does this print?", run=True,
                   code='def gen():\n    for word in ["red", "blue"]:\n'
                        '        yield word.upper()\n\n\n'
                        'for pill in gen():\n    print(pill)',
                   options=("RED / BLUE", "red / blue", "['RED', 'BLUE']"),
                   answer=0, explain="for calls next() for you."),
            Riddle("The keyword that makes a function a generator is "
                   "_____.",
                   kind="blank", answer=("yield",),
                   explain="yield, not return."),
        ],
        trial=TRIAL_5,
        victory=[Line(ORACLE, "Now you see the rain, Neo. Drop by drop.")],
    ),
    Chapter(
        id="w3c6",
        title="The Oracle's Cookies",
        exercise="ex6 · ft_data_alchemist.py",
        concept="list & dict comprehensions",
        story=[
            Line(ORACLE, "Here. Take a cookie. I promise, by the time "
                 "you're done eating it, you'll feel right as rain."),
            Line(ORACLE, "You loop, append, filter... in four lines. I can "
                 "do it in one."),
        ],
        pages=[
            Page("List comprehensions", [
                "[expression for item in collection if condition] builds a"
                " new list in one line: transform and filter.",
            ], 'names = ["Neo", "trinity", "tank"]\n'
               'print([name.capitalize() for name in names])\n'
               'print([n for n in names if n == n.capitalize()])'),
            Page("Dict (and set) comprehensions", [
                "{key: value for item in collection} builds a dict. "
                "{x for x in ...} builds a set.",
            ], 'scores = {"Neo": 900, "Tank": 100}\n'
               'average = sum(scores.values()) / len(scores)\n'
               'print({n: s for n, s in scores.items() if s > average})'),
        ],
        enemy=Enemy("Persephone", art.AGENT,
                    "I want you to kiss me... as if you were coding in one"
                    " line.",
                    "Your comprehensions are elegant. Persephone lets you "
                    "pass."),
        riddles=[
            Riddle("What does this print?", run=True,
                   code='print([n * 2 for n in [1, 2, 3]])',
                   options=("[2, 4, 6]", "[1, 2, 3, 1, 2, 3]", "12"),
                   answer=0, explain="Each element, transformed."),
            Riddle("What does this print?", run=True,
                   code='print([n for n in range(6) if n % 2 == 0])',
                   options=("[0, 2, 4]", "[1, 3, 5]", "[0, 2, 4, 6]"),
                   answer=0, explain="The if filters."),
            Riddle("What does this print?", run=True,
                   code='print({n: len(n) for n in ["Neo", "Tank"]})',
                   options=("{'Neo': 3, 'Tank': 4}", "[3, 4]",
                            "{3: 'Neo', 4: 'Tank'}"),
                   answer=0, explain="key: value for each item."),
            Riddle("What does this print?", run=True,
                   code='print({c for c in "matrix"})',
                   options=("A set of the unique letters (any order)",
                            "['m', 'a', 't', 'r', 'i', 'x']"),
                   answer=0, explain="Curly braces without ':' make a set."),
        ],
        trial=TRIAL_6,
        victory=[Line(ORACLE, "You'll do fine, Neo. You'll do fine.")],
    ),
]

BASE = {"print", "str", "int", "float"}
LISTS = BASE | {"list", "len"}

EXERCISES = [
    Exercise("ex0", "ft_command_quest.py",
             ["Show the program name, the arguments and their count."],
             LISTS, needs=["sys.argv"],
             runs=[Run(expect=["No arguments", "Total arguments: 1"]),
                   Run(["hello", "world", "42"],
                       expect=["Arguments received: 3", "Argument 3: 42",
                               "Total arguments: 4"])]),
    Exercise("ex1", "ft_score_analytics.py",
             ["Scores from argv into a list, with stats and error cases."],
             LISTS | {"sum", "max", "min"}, needs=["try", "sys.argv"],
             runs=[Run(["1500", "2300", "1800", "2100", "1950"],
                       expect=["9650", "1930.0", "2300", "1500", "800"]),
                   Run(expect=["Usage"]),
                   Run(["ab", "ac"], expect=["'ab'", "'ac'"])]),
    Exercise("ex2", "ft_coordinate_system.py",
             ["get_player_pos() asks x,y,z until valid, returns a tuple.",
              "Distances with math.sqrt()."],
             LISTS | {"tuple", "input", "round"},
             functions=["get_player_pos"], needs=["math.sqrt", "try"],
             runs=[Run(stdin="hello world\n1.0 , 2.5, 3.0\n4,abc,5\n4,5,6\n",
                       expect=["4.0311", "4.9244"])]),
    Exercise("ex3", "ft_achievement_tracker.py",
             ["gen_player_achievements() returns a random set.",
              "Union, intersection, difference across 4+ players."],
             LISTS | {"tuple", "set"},
             functions=["gen_player_achievements"]),
    Exercise("ex4", "ft_inventory_system.py",
             ["Parse item:quantity arguments into a dict, then analyse."],
             LISTS | {"tuple", "set", "dict", "sum", "round"},
             needs=["sys.argv"],
             runs=[Run(["sword:1", "potion:5", "shield:2", "armor:3",
                        "helmet:1", "sword:2", "hello", "key:value"],
                       expect=["'sword'", "'hello'", "'key'", "41.7",
                               "potion"])]),
    Exercise("ex5", "ft_data_stream.py",
             ["gen_event(): endless generator; consume_event(): yields "
              "and removes random elements."],
             LISTS | {"tuple", "next", "range"},
             functions=["gen_event", "consume_event"], needs=["yield"],
             runs=[Run(expect=["999"])]),
    Exercise("ex6", "ft_data_alchemist.py",
             ["List comprehensions for names, dict comprehensions for "
              "scores and high scores."],
             LISTS | {"sum", "round"}, needs=["listcomp", "dictcomp"]),
]

WORLD = World(
    id="w3",
    title="The Oracle",
    project="Data Quest",
    subtitle="Python collections",
    mentor=ORACLE,
    intro=[
        Line(ORACLE, "I know what you're thinking: 'am I the One?' "
             "Sorry, kiddo. Not yet."),
        Line(ORACLE, "First you have to learn to hold data: lists, tuples,"
             " sets, dicts... and the rain that never ends."),
    ],
    chapters=CHAPTERS,
    defense=[
        Riddle("Evaluator: 'Why a tuple for coordinates?'",
               options=("Tuples are faster to type",
                        "A position is a fixed group of values: immutable, "
                        "so nothing can change one part by accident"),
               answer=1, explain="Data written in stone."),
        Riddle("Evaluator: 'Why a set for achievements?'",
               options=("Each one counts once, and union/intersection/"
                        "difference answer the questions directly",
                        "Sets keep the order"),
               answer=0, explain="Sets are unordered, unique, fast."),
        Riddle("Evaluator: 'Why is gen_event() a generator and not a list "
               "of 1000 events?'",
               options=("Generators are prettier",
                        "It produces each event on demand: no memory spent"
                        " on storing them, and it can be endless"),
               answer=1, explain="That's the generator superpower."),
        Riddle("Evaluator: 'How do you skip the program name in "
               "sys.argv?'",
               options=("sys.argv[1:] or a loop starting at index 1",
                        "sys.argv.pop()"),
               answer=0, explain="Both work - be ready to discuss."),
    ],
    boss=Enemy("a hundred Agent Smiths", art.CROWD,
               "Me, me, me... me too. We are the data now, Mr. Anderson.",
               "You sort, count and stream every Smith. They scatter."),
    exercises=EXERCISES,
    outro=[Line(ORACLE, "Now go see the Keymaker. Some doors only open "
                "from the inside.")],
)
