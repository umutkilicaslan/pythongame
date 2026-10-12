"""World 1 - The Construct: Code Cultivation (object-oriented Python).

The forge trials use a `Program` class (name, power, uptime) instead of
the subject's `Plant` (name, height, age): same ideas, different names,
so you practise the concept instead of copying an answer.
"""

import ast
import inspect

from ..forge import (ForgeFailure, Spell, call, has_main_guard, lines, need,
                     no_crash, script)
from ..model import (Chapter, Enemy, Exercise, Line, Page, Riddle, Run,
                     Trial, World)
from . import art


def _make(spell: Spell, *args: object) -> object:
    """Build a Program, explaining what went wrong if we can't."""
    result = call(need(spell, "Program"), *args)
    if result.error is not None:
        raise ForgeFailure(f"Program{args} failed: {result.error!r}")
    return result.value


def _blank_program(spell: Spell, **values: object) -> object:
    """Program() with attributes set afterwards (chapters 1 and 2)."""
    result = call(need(spell, "Program"))
    if result.error is not None:
        raise ForgeFailure(
            f"Program() failed ({result.error!r}). In this chapter, create "
            "the program first and set its attributes after - constructors"
            " come in chapter 4!")
    program = result.value
    for key, value in values.items():
        setattr(program, key, value)
    return program


def _show(program: object) -> str:
    show = getattr(program, "show", None)
    if show is None:
        raise ForgeFailure(f"{type(program).__name__} has no show() method")
    result = call(show)
    if result.error is not None:
        raise ForgeFailure(f"show() crashed: {result.error!r}")
    return result.output


def _do(obj: object, name: str, *args: object) -> str:
    """Call obj.name(*args); fail politely if it's missing or crashes."""
    method = getattr(obj, name, None)
    if method is None:
        raise ForgeFailure(f"{type(obj).__name__} has no {name}() method")
    result = call(method, *args)
    if result.error is not None:
        raise ForgeFailure(f"{name}() crashed: {result.error!r}")
    return result.output


# ============================================================ chapter 0

def _c0_guard(spell: Spell) -> None:
    if not has_main_guard(spell.tree):
        raise ForgeFailure('add `if __name__ == "__main__":` at the bottom')


def _c0_import(spell: Spell) -> None:
    if spell.import_output.strip():
        raise ForgeFailure(
            "when your file is IMPORTED it already prints "
            f"{spell.import_output.strip().splitlines()[0]!r}. Move the "
            "prints inside the main guard.")


def _c0_run(spell: Spell) -> None:
    result = script(spell)
    no_crash(result, "your program")
    for word in ("Program:", "Power:", "Uptime:"):
        if word not in result.stdout:
            raise ForgeFailure(f"the output needs a line with {word!r}")


def _c0_variables(spell: Spell) -> None:
    count = sum(isinstance(node, (ast.Assign, ast.AnnAssign))
                for node in ast.walk(spell.tree))
    if count < 3:
        raise ForgeFailure("store name, power and uptime in 3 variables")


TRIAL_0 = Trial(
    id="w1c0",
    filename="w1_0_wake_up.py",
    mission=[
        "Write your first program for the Construct.",
        "Store a training program's name, power and uptime in three",
        "variables, and print them - but ONLY when the file is run",
        "directly (python3 w1_0_wake_up.py), never when it's imported.",
        "",
        "Expected output (your values can differ):",
        "  === Construct loaded ===",
        "  Program: Jump",
        "  Power: 75",
        "  Uptime: 3 days",
        "  === End of program ===",
        "",
        "Subject: ex0/ft_garden_intro.py (a plant's name, height, age).",
    ],
    skeleton='''#!/usr/bin/env python3
"""Trial: Wake up, Neo."""

# TODO: add the main guard, and inside it:
#   - store the program's name, power and uptime in 3 variables
#   - print them like the mission shows
''',
    hints=[
        'The guard is a normal if: if __name__ == "__main__":  - everything'
        " indented under it only runs when the file is executed directly.",
        "f-strings put variables inside text: print(f\"Power: {power}\")",
        "Try the shebang: chmod +x w1_0_wake_up.py then ./w1_0_wake_up.py",
    ],
    checks=[
        ("the main guard is there", _c0_guard),
        ("importing the file prints nothing", _c0_import),
        ("running it prints Program/Power/Uptime", _c0_run),
        ("the data lives in variables", _c0_variables),
    ],
)


# ============================================================ chapter 1

def _c1_show(spell: Spell) -> None:
    program = _blank_program(spell, name="Kungfu", power=88, uptime=12)
    out = _show(program)
    for value in ("Kungfu", "88", "12"):
        if value not in out:
            raise ForgeFailure(f"show() should print the {value!r} I set "
                               f"(it printed {out.strip()!r})")


def _c1_own_values(spell: Spell) -> None:
    first = _blank_program(spell, name="Dojo", power=1, uptime=2)
    second = _blank_program(spell, name="Jump", power=3, uptime=4)
    if "Dojo" not in _show(first) or "Jump" not in _show(second):
        raise ForgeFailure("each instance should show its OWN values")


def _c1_registry(spell: Spell) -> None:
    result = script(spell)
    no_crash(result, "your program")
    if len(lines(result.stdout)) < 4:
        raise ForgeFailure("show a header and at least 3 programs")


TRIAL_1 = Trial(
    id="w1c1",
    filename="w1_1_training.py",
    mission=[
        "Morpheus needs a registry of training programs.",
        "",
        "  class Program  - a blueprint for any program",
        "      attributes: name, power, uptime (set AFTER creation:",
        "                  p = Program(); p.name = 'Jump' ...)",
        "      show()      prints e.g.  Jump: 75 power, 3 days up",
        "",
        "In the main guard, create at least 3 programs and show them",
        "under a '=== Construct Program Registry ===' header.",
        "",
        "Subject: ex1/ft_garden_data.py (class Plant + show()).",
    ],
    skeleton='''class Program:
    # TODO: a show() method that prints the program's information
    pass


if __name__ == "__main__":
    print("=== Construct Program Registry ===")
    # TODO: create at least 3 programs, set their name/power/uptime,
    #       and call show() on each of them
''',
    hints=[
        "A method is a def inside the class. Its first parameter, self, is "
        "the instance: def show(self) -> None:",
        "Inside show(), reach the data with self.name, self.power, ...",
        "jump = Program()  /  jump.name = 'Jump'  /  ...  /  jump.show()",
    ],
    checks=[
        ("show() prints the program's data", _c1_show),
        ("each instance has its own values", _c1_own_values),
        ("the registry shows 3+ programs", _c1_registry),
    ],
)


# ============================================================ chapter 2

def _c2_boost(spell: Spell) -> None:
    program = _blank_program(spell, name="Jump", power=10.0, uptime=0,
                             rate=1.5)
    _do(program, "boost")
    if getattr(program, "power", None) != 11.5:
        raise ForgeFailure("with power 10.0 and rate 1.5, boost() should "
                           f"give 11.5 - got {getattr(program, 'power')!r}")


def _c2_tick(spell: Spell) -> None:
    program = _blank_program(spell, name="Jump", power=10.0, uptime=7,
                             rate=1.0)
    _do(program, "tick")
    if getattr(program, "uptime", None) != 8:
        raise ForgeFailure("tick() should add 1 day to uptime")
    if "8" not in _show(program):
        raise ForgeFailure("show() should display the new uptime")


def _c2_different(spell: Spell) -> None:
    slow = _blank_program(spell, name="A", power=0.0, uptime=0, rate=1.0)
    fast = _blank_program(spell, name="B", power=0.0, uptime=0, rate=5.0)
    _do(slow, "boost")
    _do(fast, "boost")
    if getattr(slow, "power") == getattr(fast, "power"):
        raise ForgeFailure("two programs with different rates should grow "
                           "differently")


def _c2_week(spell: Spell) -> None:
    result = script(spell)
    no_crash(result, "your program")
    if "Day 7" not in result.stdout:
        raise ForgeFailure("simulate 7 days: print '=== Day 7 ===' etc.")
    if "gained" not in result.stdout.lower():
        raise ForgeFailure("end with 'Power gained this week: ...'")


TRIAL_2 = Trial(
    id="w1c2",
    filename="w1_2_bending.py",
    mission=[
        "Programs evolve. Give yours behaviours:",
        "",
        "  class Program   attributes name, power, uptime, rate",
        "      show()      prints name, power and uptime",
        "      boost()     adds `rate` to power",
        "      tick()      adds 1 to uptime",
        "",
        "In the main guard, simulate a week: for each day, print",
        "'=== Day N ===', boost, tick and show. Finally print",
        "'Power gained this week: X' (use round()).",
        "",
        "Subject: ex2/ft_plant_growth.py (grow() and age()).",
    ],
    skeleton='''class Program:
    def show(self) -> None:
        print(f"{self.name}: {self.power} power, {self.uptime} days up")

    # TODO: boost() and tick()


if __name__ == "__main__":
    jump = Program()
    jump.name = "Jump"
    jump.power = 25.0
    jump.uptime = 30
    jump.rate = 0.8
    print("=== Construct Growth ===")
    # TODO: remember the starting power, loop over 7 days, print the gain
''',
    hints=[
        "def boost(self) -> None:  self.power += self.rate",
        "for day in range(1, 8): gives 1, 2, ... 7",
        "Store start = jump.power BEFORE the loop; the gain is "
        "round(jump.power - start, 1).",
    ],
    checks=[
        ("boost() adds the rate to the power", _c2_boost),
        ("tick() ages the program", _c2_tick),
        ("each program grows at its own rate", _c2_different),
        ("the week simulation runs", _c2_week),
    ],
)


# ============================================================ chapter 3

def _c3_ready(spell: Spell) -> None:
    program = _make(spell, "Dojo", 90.0, 12)
    out = _show(program)
    for value in ("Dojo", "90", "12"):
        if value not in out:
            raise ForgeFailure(f"show() right after construction should "
                               f"print {value!r}")


def _c3_attributes(spell: Spell) -> None:
    program = _make(spell, "Dojo", 90.0, 12)
    for attribute, value in (("name", "Dojo"), ("power", 90.0),
                             ("uptime", 12)):
        if getattr(program, attribute, None) != value:
            raise ForgeFailure(f"__init__ should set self.{attribute}")


def _c3_independent(spell: Spell) -> None:
    first = _make(spell, "One", 1.0, 1)
    second = _make(spell, "Two", 2.0, 2)
    if getattr(first, "name") == getattr(second, "name"):
        raise ForgeFailure("two programs share their name! Store values on "
                           "self, not on the class")


def _c3_batch(spell: Spell) -> None:
    result = script(spell)
    no_crash(result, "your program")
    loaded = [line for line in result.stdout.splitlines()
              if "Loaded" in line]
    if len(loaded) < 5:
        raise ForgeFailure(f"create and display 5+ programs with 'Loaded:'"
                           f" lines (found {len(loaded)})")


TRIAL_3 = Trial(
    id="w1c3",
    filename="w1_3_factory.py",
    mission=[
        "Tank needs five programs loaded - NOW. No time to set every",
        "attribute by hand: build them ready to run.",
        "",
        "  class Program",
        "      __init__(self, name: str, power: float, uptime: int)",
        "      show()  prints e.g.  Dojo: 90.0 power, 12 days up",
        "",
        "In the main guard, create at least 5 programs with different",
        "values and print each one as  'Loaded: <show output>'.",
        "",
        "Subject: ex3/ft_plant_factory.py (the constructor).",
    ],
    skeleton='''class Program:
    # TODO: __init__ that stores name, power and uptime on self

    def show(self) -> None:
        print(f"{self.name}: {self.power} power, {self.uptime} days up")


if __name__ == "__main__":
    print("=== Program Factory ===")
    # TODO: 5 programs, each displayed with a 'Loaded:' prefix
''',
    hints=[
        "def __init__(self, name: str, power: float, uptime: int) -> None:",
        "Inside: self.name = name, etc. Then Program('Dojo', 90.0, 12) "
        "works in one step.",
        "You can't change show()? Then print('Loaded: ', end='') right "
        "before calling it - end='' stops print from going to a new line.",
    ],
    checks=[
        ("a program is usable right after construction", _c3_ready),
        ("__init__ stores name, power, uptime", _c3_attributes),
        ("instances are independent", _c3_independent),
        ("5+ programs are loaded", _c3_batch),
    ],
)


# ============================================================ chapter 4

def _getter(program: object, name: str) -> object:
    method = getattr(program, name, None)
    if method is None:
        raise ForgeFailure(f"{name}() is missing")
    result = call(method)
    if result.error is not None:
        raise ForgeFailure(f"{name}() crashed: {result.error!r}")
    return result.value


def _setter(program: object, name: str, value: object) -> str:
    method = getattr(program, name, None)
    if method is None:
        raise ForgeFailure(f"{name}() is missing")
    result = call(method, value)
    if result.error is not None:
        raise ForgeFailure(f"{name}({value!r}) crashed: {result.error!r}")
    return result.output


def _c4_get(spell: Spell) -> None:
    program = _make(spell, "Jump", 15.0, 10)
    if _getter(program, "get_power") != 15.0:
        raise ForgeFailure("get_power() should return 15.0")
    if _getter(program, "get_uptime") != 10:
        raise ForgeFailure("get_uptime() should return 10")


def _c4_set(spell: Spell) -> None:
    program = _make(spell, "Jump", 15.0, 10)
    _setter(program, "set_power", 25.0)
    _setter(program, "set_uptime", 30)
    if _getter(program, "get_power") != 25.0:
        raise ForgeFailure("after set_power(25.0), get_power() is wrong")
    if _getter(program, "get_uptime") != 30:
        raise ForgeFailure("after set_uptime(30), get_uptime() is wrong")


def _c4_reject(spell: Spell) -> None:
    program = _make(spell, "Jump", 15.0, 10)
    said = _setter(program, "set_power", -5.0)
    said += _setter(program, "set_uptime", -1)
    if _getter(program, "get_power") != 15.0 or \
            _getter(program, "get_uptime") != 10:
        raise ForgeFailure("negative values must be REJECTED, leaving the "
                           "data unchanged")
    if not said.strip():
        raise ForgeFailure("print an error message when rejecting a value")


def _c4_bad_start(spell: Spell) -> None:
    result = call(need(spell, "Program"), "Glitch", -3.0, -1)
    if result.error is not None:
        raise ForgeFailure(f"Program('Glitch', -3.0, -1) crashed: "
                           f"{result.error!r}")
    program = result.value
    power = _getter(program, "get_power")
    uptime = _getter(program, "get_uptime")
    if not isinstance(power, (int, float)) or power < 0 or \
            not isinstance(uptime, int) or uptime < 0:
        raise ForgeFailure("a program created with negative values should "
                           "fall back to safe defaults (like 0)")


def _c4_protected(spell: Spell) -> None:
    program = _make(spell, "Jump", 15.0, 10)
    keys = list(vars(program))
    if any(key.startswith("_Program__") for key in keys):
        raise ForgeFailure("use the protected convention (self._power), "
                           "not name mangling (self.__power)")
    if not any(key.startswith("_") for key in keys):
        raise ForgeFailure("store the data in protected attributes, e.g. "
                           f"self._power (found: {keys})")


TRIAL_4 = Trial(
    id="w1c4",
    filename="w1_4_firewall.py",
    mission=[
        "Cypher keeps corrupting programs with impossible values.",
        "Build a firewall around the data:",
        "",
        "  class Program(name, power, uptime)",
        "      protected attributes: self._name, self._power, self._uptime",
        "      get_power(), get_uptime()          safe access",
        "      set_power(value), set_uptime(value)  validated changes:",
        "          a negative value prints an error and changes NOTHING",
        "      a program created with negative values uses 0 instead",
        "      show()",
        "",
        "Subject: ex4/ft_garden_security.py (set_height/get_height...).",
    ],
    skeleton='''class Program:
    def __init__(self, name: str, power: float, uptime: int) -> None:
        self._name = name
        # TODO: validated power and uptime (hint: reuse your setters!)

    # TODO: get_power, set_power, get_uptime, set_uptime

    def show(self) -> None:
        pass  # TODO


if __name__ == "__main__":
    print("=== Firewall ===")
    jump = Program("Jump", 15.0, 10)
    jump.set_power(-40.0)   # Cypher strikes!
''',
    hints=[
        "A setter checks before storing: if value < 0: print(...) and "
        "return. Otherwise self._power = value.",
        "In __init__, start with self._power = 0.0 then call "
        "self.set_power(power): one validation, used everywhere.",
        "The single underscore is a promise between developers, not a lock."
        " Name mangling (__power) is NOT what the subject wants.",
    ],
    checks=[
        ("getters return the values", _c4_get),
        ("setters change valid values", _c4_set),
        ("negative values are rejected with a message", _c4_reject),
        ("bad starting values fall back to defaults", _c4_bad_start),
        ("data lives in protected attributes", _c4_protected),
    ],
)


# ============================================================ chapter 5

def _c5_family(spell: Spell) -> None:
    program = need(spell, "Program")
    for name in ("Agent", "Sentinel", "Exile"):
        cls = need(spell, name)
        if not (inspect.isclass(cls) and issubclass(cls, program)):
            raise ForgeFailure(f"{name} must inherit from Program")


def _c5_agent(spell: Spell) -> None:
    result = call(need(spell, "Agent"), "Smith", 50.0, 10, "Smith-01")
    if result.error is not None:
        raise ForgeFailure(f"Agent('Smith', 50.0, 10, 'Smith-01') failed: "
                           f"{result.error!r}")
    agent = result.value
    if getattr(agent, "name", None) != "Smith":
        raise ForgeFailure("agent.name is not set: call super().__init__")
    before = _show(agent)
    for value in ("Smith", "50", "Smith-01"):
        if value not in before:
            raise ForgeFailure(f"Agent.show() should include {value!r}: "
                               "the parent's info AND the codename")
    _do(agent, "hunt")
    if _show(agent) == before:
        raise ForgeFailure("after hunt(), show() should look different")


def _c5_sentinel(spell: Spell) -> None:
    result = call(need(spell, "Sentinel"), "Squid", 80.0, 3, 12)
    if result.error is not None:
        raise ForgeFailure(f"Sentinel('Squid', 80.0, 3, 12) failed: "
                           f"{result.error!r}")
    scan = _do(result.value, "scan")
    if "Squid" not in scan or "12" not in scan:
        raise ForgeFailure("scan() should print the name and tentacles")


def _c5_exile(spell: Spell) -> None:
    result = call(need(spell, "Exile"), "Merovingian", 30.0, 1000,
                  "Club Hel")
    if result.error is not None:
        raise ForgeFailure(f"Exile(...) failed: {result.error!r}")
    exile = result.value
    if getattr(exile, "influence", None) != 0:
        raise ForgeFailure("an Exile's influence starts at 0")
    _do(exile, "boost")
    if getattr(exile, "power") != 31.0 or getattr(exile, "influence") != 1:
        raise ForgeFailure("Exile.boost() should do the normal boost (+1.0 "
                           "power) AND add 1 influence - use super()")
    _do(exile, "tick")
    if getattr(exile, "uptime") != 1001 or getattr(exile, "influence") != 2:
        raise ForgeFailure("Exile.tick() should age it AND add influence")


def _c5_super(spell: Spell) -> None:
    for node in ast.walk(spell.tree):
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "super":
            return
    raise ForgeFailure("reuse the parent's code with super()")


TRIAL_5 = Trial(
    id="w1c5",
    filename="w1_5_programs.py",
    mission=[
        "Agents, Sentinels and Exiles are all Programs - with extras.",
        "",
        "  class Program(name, power, uptime)",
        "      show(), boost() (+1.0 power), tick() (+1 uptime)",
        "  class Agent(Program)     + codename: str",
        "      hunt()  starts hunting; show() then says so",
        "  class Sentinel(Program)  + tentacles: int",
        "      scan()  prints e.g. 'Sentinel Squid scans with 12 tentacles'",
        "  class Exile(Program)     + hideout: str, influence starts at 0",
        "      boost() and tick() also add 1 influence",
        "",
        "Each show() prints the Program lines + its own extras.",
        "Don't repeat the Program code: use super() everywhere.",
        "",
        "Subject: ex5/ft_plant_types.py (Flower, Tree, Vegetable).",
    ],
    skeleton='''class Program:
    def __init__(self, name: str, power: float, uptime: int) -> None:
        self.name = name
        self.power = power
        self.uptime = uptime

    def show(self) -> None:
        print(f"{self.name}: {self.power} power, {self.uptime} days up")

    def boost(self) -> None:
        self.power += 1.0

    def tick(self) -> None:
        self.uptime += 1


class Agent(Program):
    def __init__(self, name: str, power: float, uptime: int,
                 codename: str) -> None:
        # TODO: let Program do its part, then store the codename
        pass


# TODO: Sentinel and Exile


if __name__ == "__main__":
    print("=== Programs of the Matrix ===")
''',
    hints=[
        "super().__init__(name, power, uptime) runs Program's constructor "
        "on this new object.",
        "In Agent.show(): super().show() first, then print the extra lines.",
        "Exile.boost(): super().boost() then self.influence += 1.",
    ],
    checks=[
        ("Agent, Sentinel and Exile inherit from Program", _c5_family),
        ("Agent: parent data + codename + hunt()", _c5_agent),
        ("Sentinel.scan() works", _c5_sentinel),
        ("Exile gains influence when boosted or ticked", _c5_exile),
        ("super() is used", _c5_super),
    ],
)


# ============================================================ chapter 6

def _c6_static(spell: Spell) -> None:
    program = need(spell, "Program")
    method = getattr(program, "is_legacy", None)
    if not isinstance(inspect.getattr_static(program, "is_legacy", None),
                      staticmethod) or method is None:
        raise ForgeFailure("is_legacy must be a @staticmethod of Program")
    if method(30) is not False or method(400) is not True:
        raise ForgeFailure("is_legacy(30) should be False, is_legacy(400) "
                           "True (more than a year)")


def _c6_anonymous(spell: Spell) -> None:
    program = need(spell, "Program")
    if not isinstance(inspect.getattr_static(program, "anonymous", None),
                      classmethod):
        raise ForgeFailure("anonymous must be a @classmethod of Program")
    result = call(program.anonymous)
    if result.error is not None or not isinstance(result.value, program):
        raise ForgeFailure(f"Program.anonymous() should return a Program "
                           f"(got {result.value!r} / {result.error!r})")
    if "Unknown" not in _show(result.value):
        raise ForgeFailure("the anonymous program is 'Unknown program'")


def _c6_stats(spell: Spell) -> None:
    program = need(spell, "Program")
    if not inspect.isclass(getattr(program, "Stats", None)):
        raise ForgeFailure("Program needs a nested class Stats")
    jump = _make(spell, "Jump", 1.0, 1)
    _do(jump, "boost")
    _do(jump, "show")
    out = call(need(spell, "display_stats"), jump).output
    if "1 boost, 0 tick, 1 show" not in out:
        raise ForgeFailure("after 1 boost and 1 show, display_stats should "
                           f"print 'Stats: 1 boost, 0 tick, 1 show' (got "
                           f"{out.strip()!r})")


def _c6_clone(spell: Spell) -> None:
    clone = need(spell, "Clone")
    if not issubclass(clone, need(spell, "Agent")):
        raise ForgeFailure("Clone must inherit from Agent")
    result = call(clone, "Smith", 50.0, 10, "Smith")
    if result.error is not None:
        raise ForgeFailure(f"Clone('Smith', 50.0, 10, 'Smith') failed: "
                           f"{result.error!r}")
    smith = result.value
    if "Copies: 0" not in _show(smith):
        raise ForgeFailure("Clone.show() should print 'Copies: 0' at first")
    _do(smith, "hunt")
    if "Copies: 1" not in _show(smith):
        raise ForgeFailure("after hunt(), a Clone shows 'Copies: 1'")


def _c6_sentinel(spell: Spell) -> None:
    result = call(need(spell, "Sentinel"), "Squid", 80.0, 3, 12)
    if result.error is not None:
        raise ForgeFailure(f"Sentinel(...) failed: {result.error!r}")
    _do(result.value, "scan")
    out = call(need(spell, "display_stats"), result.value).output
    if "1 scan" not in out:
        raise ForgeFailure("a Sentinel's stats also count scans: '1 scan'")


TRIAL_6 = Trial(
    id="w1c6",
    filename="w1_6_architect.py",
    mission=[
        "The Architect measures everything. Show him you can too.",
        "",
        "  class Program(name, power, uptime)  show(), boost(), tick()",
        "      @staticmethod is_legacy(uptime: int) -> bool   (> 365 days)",
        "      @classmethod anonymous(cls)  -> 'Unknown program', 0.0, 0",
        "      class Stats (nested!) counting boost/tick/show calls in",
        "          protected attributes, with display() printing",
        "          'Stats: 1 boost, 0 tick, 1 show'",
        "  class Agent(Program)    + codename, hunt()",
        "  class Clone(Agent)      + copies (0; each hunt() adds 1),",
        "                           show() adds 'Copies: N'",
        "  class Sentinel(Program) + tentacles, scan(); its stats also",
        "                           print ' 1 scan'",
        "  def display_stats(program: Program) -> None   (NOT in a class)",
        "",
        "Subject: ex6/ft_garden_analytics.py.",
    ],
    skeleton='''class Program:
    class Stats:
        def __init__(self) -> None:
            self._boosts = 0
            # TODO: ticks and shows

        def display(self) -> None:
            pass  # TODO

    def __init__(self, name: str, power: float, uptime: int) -> None:
        self.name = name
        self.power = power
        self.uptime = uptime
        self._stats = Program.Stats()

    # TODO: show, boost, tick (each one counts itself in self._stats)
    # TODO: is_legacy (static) and anonymous (class method)


# TODO: Agent, Clone, Sentinel


def display_stats(program: Program) -> None:
    pass  # TODO


if __name__ == "__main__":
    print("=== The Architect's Analytics ===")
''',
    hints=[
        "@staticmethod above def is_legacy(uptime: int) -> bool: - no self.",
        "@classmethod: def anonymous(cls) -> 'Program': return cls("
        "'Unknown program', 0.0, 0)",
        "Sentinel can count scans in its own Stats subclass "
        "(class SentinelStats(Program.Stats)) - or any design you can "
        "explain. display_stats just calls program._stats.display()... or "
        "better, a public method that does.",
    ],
    checks=[
        ("is_legacy is a working static method", _c6_static),
        ("anonymous() is a class method", _c6_anonymous),
        ("the nested Stats class counts calls", _c6_stats),
        ("Clone inherits from Agent and copies itself", _c6_clone),
        ("Sentinels count their scans", _c6_sentinel),
    ],
)


# ============================================================ the story

MORPHEUS = "Morpheus"

CHAPTERS = [
    Chapter(
        id="w1c0",
        title="Wake Up, Neo",
        exercise="ex0 · ft_garden_intro.py",
        concept="program structure · if __name__ == \"__main__\"",
        story=[
            Line("Trinity", "The Matrix has you, Neo."),
            Line(MORPHEUS, "You've felt it your whole life: something is "
                 "wrong with the world. Programs run, and you don't know "
                 "where they start."),
            Line(MORPHEUS, "Every Python program has a starting point. "
                 "Before you can bend the rules, you must see where they "
                 "begin."),
            Line("Tank", "Loading the Construct... Everything you see here "
                 "is code."),
        ],
        pages=[
            Page("Where a program begins", [
                "Python reads your file from top to bottom and runs every "
                "line it finds.",
                "When you run a file directly (python3 file.py), Python "
                "sets a special variable, __name__, to the text "
                "\"__main__\".",
            ], 'print("This file is called:", __name__)'),
            Page("The main guard", [
                "When another file IMPORTS yours, __name__ is the module's "
                "name instead - so the code under the guard does NOT run.",
                "That's why we put the 'start the program' code under "
                "if __name__ == \"__main__\":. Your file can then be run "
                "AND reused by others.",
            ], 'def show_info() -> None:\n'
               '    print("Program: Jump")\n'
               '\n'
               '\n'
               'if __name__ == "__main__":\n'
               '    show_info()   # only when run directly'),
            Page("Variables, f-strings and the shebang", [
                "Variables hold data: name = \"Jump\", power = 75.",
                "f-strings put them inside text: f\"Power: {power}\".",
                "A first line #!/usr/bin/env python3 (the shebang) tells "
                "your system which program runs the file. After "
                "chmod +x file.py you can run it as ./file.py. The "
                "evaluation will ask you to add it live!",
            ], 'name = "Jump"\n'
               'power = 75\n'
               'print(f"Program: {name}")\n'
               'print(f"Power: {power}")'),
        ],
        enemy=Enemy("the Sleep Daemon", art.DAEMON,
                    "Go back to sleep, Neo... none of this is real...",
                    "The Sleep Daemon dissolves. You are awake."),
        riddles=[
            Riddle("What does this print when the file is run directly?",
                   code='print(__name__)',
                   options=("__main__", "snippet", "None", "main"),
                   answer=0, run=True,
                   explain="Run directly, a file's __name__ is always "
                           "\"__main__\"."),
            Riddle("a.py ends with  if __name__ == \"__main__\": "
                   "print(\"hi\").  Another file does  import a.  "
                   "What is printed?",
                   options=("hi", "Nothing: when imported, __name__ is "
                            "\"a\", so the guard is False", "An error"),
                   answer=1,
                   explain="The guard protects code from running on "
                           "import. That's the whole point."),
            Riddle("Fill the blank:   if __name__ == \"________\":",
                   kind="blank", answer=("__main__",),
                   explain="Two underscores on each side: __main__."),
            Riddle("What does this print?",
                   code='name = "Neo"\nlevel = 1\n'
                        'print(f"{name} is level {level}")',
                   options=("{name} is level {level}", "Neo is level 1",
                            "name is level level"),
                   answer=1, run=True,
                   explain="The f before the quotes makes Python replace "
                           "{...} with the values."),
            Riddle("What does the line  #!/usr/bin/env python3  do?",
                   options=("Nothing, it's a comment",
                            "It tells the system which interpreter runs "
                            "the file when you execute it as ./file.py",
                            "It imports Python 3"),
                   answer=1,
                   explain="For Python it IS a comment, but your shell "
                           "reads it to know how to run the file."),
        ],
        trial=TRIAL_0,
        victory=[Line(MORPHEUS, "Now you know where a program begins. "
                      "Next: what it is made of.")],
    ),
    Chapter(
        id="w1c1",
        title="The Training Program",
        exercise="ex1 · ft_garden_data.py",
        concept="classes · instances · attributes · methods",
        story=[
            Line(MORPHEUS, "This is the Construct, our loading program. We "
                 "can load anything: clothes, equipment, training "
                 "simulations."),
            Line("Tank", "Every training sim follows the same blueprint. "
                 "Name, power, uptime..."),
            Line(MORPHEUS, "Write the blueprint once. That's a class. Every "
                 "program built from it is an instance."),
        ],
        pages=[
            Page("A class is a blueprint", [
                "class Program: describes what every program looks like.",
                "Program() builds one real program from it: an instance "
                "(an object). Each instance carries its own attributes.",
            ], 'class Program:\n'
               '    pass\n'
               '\n'
               '\n'
               'jump = Program()        # an instance\n'
               'jump.name = "Jump"      # its attributes\n'
               'jump.power = 75\n'
               'print(jump.name, jump.power)'),
            Page("Methods and self", [
                "A method is a function inside a class. Its first "
                "parameter, self, is the instance it was called on.",
                "jump.show() is really Program.show(jump).",
            ], 'class Program:\n'
               '    def show(self) -> None:\n'
               '        print(f"{self.name}: {self.power} power")\n'
               '\n'
               '\n'
               'jump = Program()\n'
               'jump.name = "Jump"\n'
               'jump.power = 75\n'
               'jump.show()'),
            Page("Why bother?", [
                "Three variables per program is fine for one program. For a "
                "hundred, you'd juggle three hundred variables!",
                "A class keeps each program's data together, with the code "
                "that uses it. Naming rule from the subject: classes in "
                "PascalCase (TrainingProgram), functions and variables in "
                "snake_case (show_info).",
            ]),
        ],
        enemy=Enemy("the Sparring Program", art.AGENT,
                    "Show me what you've got, Neo.",
                    "\"He's fast,\" whispers Mouse. \"Faster than anyone "
                    "we've seen.\""),
        riddles=[
            Riddle("What does this print?",
                   code='class Program:\n    pass\n\n\n'
                        'a = Program()\nb = Program()\n'
                        'a.name = "Neo"\nb.name = "Trinity"\nprint(a.name)',
                   options=("Neo", "Trinity", "An error"),
                   answer=0, run=True,
                   explain="a and b are two different objects, each with "
                           "its own attributes."),
            Riddle("In  def show(self) -> None:,  what is self?",
                   options=("The class itself",
                            "The instance the method was called on",
                            "A keyword you must type when calling show()"),
                   answer=1,
                   explain="jump.show() passes jump as self automatically."),
            Riddle("What happens here?",
                   code='class Program:\n'
                        '    def show(self) -> None:\n'
                        '        print(self.name)\n\n\n'
                        'p = Program()\np.show()',
                   options=("It prints nothing", "It prints None",
                            "It crashes: p has no attribute 'name'"),
                   answer=2, run=True,
                   explain="Attributes only exist once you set them. "
                           "(Constructors will fix that in chapter 4.)"),
            Riddle("A function defined inside a class is called a ______.",
                   kind="blank", answer=("method", "methods"),
                   explain="Functions in classes are methods."),
            Riddle("Which class name follows the subject's convention?",
                   options=("class training_program",
                            "class TrainingProgram",
                            "class TRAINING_PROGRAM"),
                   answer=1,
                   explain="PascalCase for classes, snake_case for the "
                           "rest."),
        ],
        trial=TRIAL_1,
        victory=[Line(MORPHEUS, "Good. One blueprint, many programs.")],
    ),
    Chapter(
        id="w1c2",
        title="Bending the Rules",
        exercise="ex2 · ft_plant_growth.py",
        concept="methods that change state · simulation loops",
        story=[
            Line(MORPHEUS, "Do you think that's air you're breathing now?"),
            Line(MORPHEUS, "Programs in the Matrix are not frozen. They "
                 "grow, they age, they change."),
            Line("Tank", "The Jump program needs to evolve over a week. "
                 "Give it behaviours."),
        ],
        pages=[
            Page("Methods that change the object", [
                "A method can modify its own instance through self.",
                "Different instances can behave differently, if their "
                "attributes differ - like a personal growth rate.",
            ], 'class Program:\n'
               '    def boost(self) -> None:\n'
               '        self.power = self.power + self.rate\n'
               '\n'
               '    def tick(self) -> None:\n'
               '        self.uptime += 1'),
            Page("Simulating a week", [
                "range(1, 8) gives 1, 2, ... 7. Remember the starting value "
                "BEFORE the loop to compute the total change after it.",
                "Floats are not exact in binary: round(x, 1) keeps the "
                "display clean.",
            ], 'start = jump.power\n'
               'for day in range(1, 8):\n'
               '    print(f"=== Day {day} ===")\n'
               '    jump.boost()\n'
               '    jump.tick()\n'
               '    jump.show()\n'
               'print(f"Gained: {round(jump.power - start, 1)}")'),
        ],
        enemy=Enemy("the Jump Program", art.SENTINEL,
                    "Nobody makes the first jump...",
                    "You land on the other roof. Morpheus smiles."),
        riddles=[
            Riddle("What does this print?",
                   code='class Counter:\n'
                        '    def inc(self) -> None:\n'
                        '        self.count += 1\n\n\n'
                        'c = Counter()\nc.count = 0\nc.inc()\nc.inc()\n'
                        'print(c.count)',
                   options=("0", "1", "2", "An error"),
                   answer=2, run=True,
                   explain="Each call changes the same object's count."),
            Riddle("And with two counters?",
                   code='class Counter:\n'
                        '    def inc(self) -> None:\n'
                        '        self.count += 1\n\n\n'
                        'a = Counter()\nb = Counter()\n'
                        'a.count = 0\nb.count = 0\n'
                        'a.inc()\na.inc()\nb.inc()\nprint(a.count, b.count)',
                   options=("2 1", "3 3", "1 1"),
                   answer=0, run=True,
                   explain="Each instance has its own state."),
            Riddle("What does list(range(1, 8)) contain?",
                   code='print(list(range(1, 8)))',
                   options=("[1, 2, 3, 4, 5, 6, 7, 8]",
                            "[1, 2, 3, 4, 5, 6, 7]",
                            "[0, 1, 2, 3, 4, 5, 6, 7]"),
                   answer=1, run=True,
                   explain="The end of a range is excluded."),
            Riddle("Why does the subject allow round()?",
                   code='print(30.6 - 25.0)',
                   options=("It prints 5.6, round() is just style",
                            "It prints 5.600000000000001: floats aren't "
                            "exact, round() cleans the display"),
                   answer=1, run=True,
                   explain="Computers store floats in binary, so tiny "
                           "errors appear."),
            Riddle("Inside a method, the object itself is reached through "
                   "____.",
                   kind="blank", answer=("self",),
                   explain="self.power, self.uptime..."),
        ],
        trial=TRIAL_2,
        victory=[Line(MORPHEUS, "You're beginning to believe.")],
    ),
    Chapter(
        id="w1c3",
        title="The Program Factory",
        exercise="ex3 · ft_plant_factory.py",
        concept="__init__ · constructors · instantiation",
        story=[
            Line("Tank", "Morpheus wants five new sims loaded. Setting every"
                 " attribute by hand takes forever."),
            Line("Mouse", "I made a program of a woman in a red dress. "
                 "Took me ages to set her up."),
            Line(MORPHEUS, "Then build them ready to run. The moment a "
                 "program is born, it should know who it is."),
        ],
        pages=[
            Page("__init__, the constructor", [
                "__init__ runs automatically when an instance is created. "
                "Whatever you give to Program(...) arrives as its "
                "parameters.",
                "Creation (instantiation) and setup (initialization) now "
                "happen in one step.",
            ], 'class Program:\n'
               '    def __init__(self, name: str, power: float,\n'
               '                 uptime: int) -> None:\n'
               '        self.name = name\n'
               '        self.power = power\n'
               '        self.uptime = uptime\n'
               '\n'
               '\n'
               'jump = Program("Jump", 75.0, 3)\n'
               'print(jump.name)'),
            Page("Many programs at once", [
                "A list of instances and a loop: the factory is open.",
                "self.name = name stores the PARAMETER name in the "
                "ATTRIBUTE name of this object - same word, two things.",
            ], 'programs = [Program("Jump", 75.0, 3),\n'
               '            Program("Dojo", 90.0, 12)]\n'
               'for program in programs:\n'
               '    print(program.name)'),
        ],
        enemy=Enemy("the Woman in the Red Dress", art.CROWD,
                    "Were you listening to me, Neo? Or were you looking at "
                    "the woman in the red dress?",
                    "\"Look again,\" says Morpheus. It was an Agent. You "
                    "weren't fooled."),
        riddles=[
            Riddle("What does this print?",
                   code='class Program:\n'
                        '    def __init__(self) -> None:\n'
                        '        print("born")\n\n\n'
                        'a = Program()\nb = Program()',
                   options=("born", "born / born", "Nothing"),
                   answer=1, run=True,
                   explain="__init__ runs once per new instance."),
            Riddle("What happens here?",
                   code='class Program:\n'
                        '    def __init__(self, name: str, power: float)'
                        ' -> None:\n'
                        '        self.name = name\n'
                        '        self.power = power\n\n\n'
                        'p = Program("Jump")',
                   options=("p.power is None", "It crashes: missing 1 "
                            "required argument 'power'", "p.power is 0"),
                   answer=1, run=True,
                   explain="The constructor's parameters are required "
                           "unless they have a default value."),
            Riddle("What does this print?",
                   code='class Program:\n'
                        '    def __init__(self, name: str, power: float = '
                        '0.0) -> None:\n'
                        '        self.name = name\n'
                        '        self.power = power\n\n\n'
                        'print(Program("Ghost").power)',
                   options=("0.0", "None", "An error"),
                   answer=0, run=True,
                   explain="Default values make parameters optional."),
            Riddle("The constructor method is named ________.",
                   kind="blank", answer=("__init__",),
                   explain="Two underscores, init, two underscores."),
        ],
        trial=TRIAL_3,
        victory=[Line("Tank", "Five programs loaded in one second. "
                      "Morpheus is impressed.")],
    ),
    Chapter(
        id="w1c4",
        title="The Firewall",
        exercise="ex4 · ft_garden_security.py",
        concept="encapsulation · protected attributes · getters/setters",
        story=[
            Line("Tank", "Someone set the Jump program's power to -40. "
                 "That's not even possible."),
            Line("Trinity", "Cypher. He's been touching data he shouldn't."),
            Line(MORPHEUS, "A program anyone can corrupt WILL be corrupted."
                 " Protect its data. Let the world talk to it only through "
                 "doors you control."),
        ],
        pages=[
            Page("Protected attributes", [
                "A single underscore, self._power, means 'internal - don't "
                "touch it from outside, use the methods'.",
                "Python does not block access: it's a convention every "
                "Python developer respects. A double underscore "
                "(self.__power) triggers name mangling - the subject asks "
                "for the protected convention, NOT mangling.",
            ]),
            Page("Getters and setters", [
                "A setter validates before storing. A getter gives safe "
                "read access. The constructor can reuse the setter, so the"
                " validation lives in one place.",
            ], 'class Program:\n'
               '    def __init__(self, name: str, power: float) -> None:\n'
               '        self._name = name\n'
               '        self._power = 0.0\n'
               '        self.set_power(power)\n'
               '\n'
               '    def set_power(self, power: float) -> None:\n'
               '        if power < 0:\n'
               '            print(f"{self._name}: Error, power can\'t be "\n'
               '                  "negative")\n'
               '            return\n'
               '        self._power = power\n'
               '\n'
               '    def get_power(self) -> float:\n'
               '        return self._power\n'
               '\n'
               '\n'
               'jump = Program("Jump", 15.0)\n'
               'jump.set_power(-40.0)\n'
               'print(jump.get_power())'),
        ],
        enemy=Enemy("Cypher", art.AGENT,
                    "Ignorance is bliss. Let me just... change a few "
                    "values.",
                    "Your setters reject every corrupt value. Cypher's "
                    "plan fails."),
        riddles=[
            Riddle("What does this print?",
                   code='class Program:\n'
                        '    def __init__(self) -> None:\n'
                        '        self._power = 75.0\n\n'
                        '    def set_power(self, power: float) -> None:\n'
                        '        if power < 0:\n'
                        '            print("rejected")\n'
                        '            return\n'
                        '        self._power = power\n\n'
                        '    def get_power(self) -> float:\n'
                        '        return self._power\n\n\n'
                        'p = Program()\np.set_power(-5.0)\n'
                        'print(p.get_power())',
                   options=("rejected / 75.0", "rejected / -5.0", "75.0"),
                   answer=0, run=True,
                   explain="return leaves the setter before storing."),
            Riddle("What does the single underscore in _power mean?",
                   options=("Python makes it private and blocks access",
                            "A convention: 'internal, go through the "
                            "methods'", "It's a syntax error"),
                   answer=1,
                   explain="It's a promise between developers, not a lock."),
            Riddle("So what happens here?",
                   code='class Program:\n'
                        '    def __init__(self) -> None:\n'
                        '        self._power = 75.0\n\n\n'
                        'p = Program()\np._power = -10.0\nprint(p._power)',
                   options=("An AttributeError", "-10.0"),
                   answer=1, run=True,
                   explain="Python allows it. Respecting the underscore is "
                           "YOUR job (and your peers' at evaluation)."),
            Riddle("And with two underscores?",
                   code='class Program:\n'
                        '    def __init__(self) -> None:\n'
                        '        self.__power = 75.0\n\n\n'
                        'p = Program()\nprint(p.__power)',
                   options=("75.0", "It crashes: the name was mangled "
                            "to _Program__power"),
                   answer=1, run=True,
                   explain="That's name mangling, which the subject says "
                           "NOT to use here."),
            Riddle("A method that returns a protected value is called a "
                   "______.",
                   kind="blank", answer=("getter", "getters"),
                   explain="get_power() is a getter, set_power() a setter."),
        ],
        trial=TRIAL_4,
        victory=[Line("Trinity", "Nobody corrupts our programs now.")],
    ),
    Chapter(
        id="w1c5",
        title="Agents, Sentinels and Exiles",
        exercise="ex5 · ft_plant_types.py",
        concept="inheritance · super() · overriding",
        story=[
            Line(MORPHEUS, "The Matrix is full of programs. Agents. "
                 "Sentinels. Exiles."),
            Line(MORPHEUS, "Different... but every one of them is still a "
                 "program. They share a body of code."),
            Line("Trinity", "Write the common part once, in the parent. "
                 "The children only add what's special."),
        ],
        pages=[
            Page("Inheritance", [
                "class Agent(Program): means an Agent IS a Program. It gets "
                "all of Program's methods for free.",
            ], 'class Program:\n'
               '    def hello(self) -> None:\n'
               '        print("I am a program")\n'
               '\n'
               '\n'
               'class Agent(Program):\n'
               '    pass\n'
               '\n'
               '\n'
               'Agent().hello()'),
            Page("super() and overriding", [
                "A child can redefine (override) a method. Inside it, "
                "super() reaches the parent's version, so you can extend "
                "instead of copy-pasting.",
            ], 'class Agent(Program):\n'
               '    def __init__(self, name: str, power: float,\n'
               '                 uptime: int, codename: str) -> None:\n'
               '        super().__init__(name, power, uptime)\n'
               '        self.codename = codename\n'
               '\n'
               '    def show(self) -> None:\n'
               '        super().show()          # the parent\'s lines\n'
               '        print(f" Codename: {self.codename}")'),
        ],
        enemy=Enemy("Agent Brown", art.AGENT,
                    "We are all programs, Mr. Anderson. Some of us just "
                    "have... extras.",
                    "Agent Brown's code is just Program + a few lines. You"
                    " see right through it."),
        riddles=[
            Riddle("What does this print?",
                   code='class Program:\n'
                        '    def hello(self) -> None:\n'
                        '        print("program")\n\n\n'
                        'class Agent(Program):\n    pass\n\n\n'
                        'Agent().hello()',
                   options=("program", "Nothing", "An error: Agent has no "
                            "hello"),
                   answer=0, run=True,
                   explain="Agent inherits hello() from Program."),
            Riddle("With an override?",
                   code='class Program:\n'
                        '    def hello(self) -> None:\n'
                        '        print("program")\n\n\n'
                        'class Agent(Program):\n'
                        '    def hello(self) -> None:\n'
                        '        print("agent")\n\n\n'
                        'Agent().hello()',
                   options=("program", "agent", "program / agent"),
                   answer=1, run=True,
                   explain="The child's version wins."),
            Riddle("And with super()?",
                   code='class Program:\n'
                        '    def hello(self) -> None:\n'
                        '        print("program")\n\n\n'
                        'class Agent(Program):\n'
                        '    def hello(self) -> None:\n'
                        '        super().hello()\n'
                        '        print("agent")\n\n\n'
                        'Agent().hello()',
                   options=("agent / program", "program / agent", "agent"),
                   answer=1, run=True,
                   explain="super().hello() runs the parent's code first."),
            Riddle("What happens if the child's __init__ forgets super()?",
                   code='class Program:\n'
                        '    def __init__(self, name: str) -> None:\n'
                        '        self.name = name\n\n\n'
                        'class Agent(Program):\n'
                        '    def __init__(self, name: str, code: str) -> '
                        'None:\n'
                        '        self.code = code\n\n\n'
                        'smith = Agent("Smith", "S-01")\nprint(smith.name)',
                   options=("Smith", "It crashes: 'name' was never set",
                            "None"),
                   answer=1, run=True,
                   explain="Python does NOT call the parent's __init__ for "
                           "you once you override it."),
            Riddle("isinstance(Agent(), Program) is...",
                   kind="blank", answer=("True",),
                   explain="An Agent IS a Program."),
        ],
        trial=TRIAL_5,
        victory=[Line(MORPHEUS, "One body of code, many faces. That's "
                      "inheritance.")],
    ),
    Chapter(
        id="w1c6",
        title="The Architect",
        exercise="ex6 · ft_garden_analytics.py",
        concept="static/class methods · nested classes · chains",
        story=[
            Line("The Architect", "Hello, Neo. I am the Architect. I "
                 "created the Matrix. And I measure... everything."),
            Line("The Architect", "Every call. Every change. Every program."
                 " Can you?"),
            Line(MORPHEUS, "Everything you learned fits together here. "
                 "Show him."),
        ],
        pages=[
            Page("Static methods", [
                "A @staticmethod belongs to the class but needs no "
                "instance: no self. Use it for helpers related to the "
                "class.",
            ], 'class Program:\n'
               '    @staticmethod\n'
               '    def is_legacy(uptime: int) -> bool:\n'
               '        return uptime > 365\n'
               '\n'
               '\n'
               'print(Program.is_legacy(400))'),
            Page("Class methods", [
                "A @classmethod receives the class itself as cls. It's the "
                "classic way to offer another way to build objects.",
                "Called on a subclass, cls is that subclass!",
            ], 'class Program:\n'
               '    def __init__(self, name: str) -> None:\n'
               '        self.name = name\n'
               '\n'
               '    @classmethod\n'
               '    def anonymous(cls) -> "Program":\n'
               '        return cls("Unknown program")\n'
               '\n'
               '\n'
               'print(Program.anonymous().name)'),
            Page("Nested classes and chains", [
                "A class defined inside another groups a helper with its "
                "owner: Program.Stats. Each program holds its own Stats "
                "object.",
                "Chains work too: Clone(Agent) and Agent(Program), so a "
                "Clone is an Agent AND a Program. A plain function like "
                "display_stats(program) then works for ANY of them.",
            ], 'class Program:\n'
               '    class Stats:\n'
               '        def __init__(self) -> None:\n'
               '            self._shows = 0\n'
               '\n'
               '    def __init__(self) -> None:\n'
               '        self._stats = Program.Stats()'),
        ],
        enemy=Enemy("the Architect", art.ARCHITECT,
                    "Your life is the sum of a remainder of an unbalanced "
                    "equation...",
                    "\"Ergo,\" the Architect stammers, \"you... understand "
                    "the system.\""),
        riddles=[
            Riddle("What does this print?",
                   code='class Program:\n'
                        '    @staticmethod\n'
                        '    def is_legacy(uptime: int) -> bool:\n'
                        '        return uptime > 365\n\n\n'
                        'print(Program.is_legacy(30), '
                        'Program.is_legacy(400))',
                   options=("False True", "True False", "An error: no "
                            "instance"),
                   answer=0, run=True,
                   explain="Static methods are called on the class."),
            Riddle("What does this print?",
                   code='class Program:\n'
                        '    @classmethod\n'
                        '    def make(cls) -> "Program":\n'
                        '        return cls()\n\n\n'
                        'class Agent(Program):\n    pass\n\n\n'
                        'print(type(Agent.make()).__name__)',
                   options=("Program", "Agent", "cls"),
                   answer=1, run=True,
                   explain="cls is whatever class you called it on."),
            Riddle("What does this print?",
                   code='class Program:\n'
                        '    class Stats:\n'
                        '        count = 0\n\n\n'
                        'print(Program.Stats.count)',
                   options=("0", "An error", "Stats"),
                   answer=0, run=True,
                   explain="A nested class is reached through its owner."),
            Riddle("Which kind of method needs neither self nor cls?",
                   options=("A class method", "A static method",
                            "An instance method"),
                   answer=1,
                   explain="Static methods are plain functions living in a "
                           "class."),
            Riddle("What does this print?",
                   code='class Program:\n    pass\n\n\n'
                        'class Agent(Program):\n    pass\n\n\n'
                        'class Clone(Agent):\n    pass\n\n\n'
                        'print(isinstance(Clone(), Program))',
                   options=("True", "False"),
                   answer=0, run=True,
                   explain="Inheritance chains: a Clone is an Agent, and "
                           "an Agent is a Program."),
        ],
        trial=TRIAL_6,
        victory=[Line("The Architect", "...Interesting."),
                 Line(MORPHEUS, "You've mastered the Construct.")],
    ),
]

AUTH = {"print"}
GROW = {"print", "range", "round"}

EXERCISES = [
    Exercise("ex0", "ft_garden_intro.py",
             ["Store a plant's name, height and age in variables.",
              'Print them inside if __name__ == "__main__":'],
             AUTH, needs=["main_guard"],
             runs=[Run(expect=["Plant", "Height", "Age"])]),
    Exercise("ex1", "ft_garden_data.py",
             ["class Plant (name, height, age) + show().",
              "At least 3 plants displayed."],
             AUTH, classes={"Plant": ""}, needs=["main_guard"]),
    Exercise("ex2", "ft_plant_growth.py",
             ["Plant gets grow() and age() methods.",
              "Simulate a week and display the total growth."],
             GROW, classes={"Plant": ""}, needs=["main_guard"],
             runs=[Run(expect=["Day 7"])]),
    Exercise("ex3", "ft_plant_factory.py",
             ["Plants created with their data via __init__.",
              "At least 5 plants displayed."],
             GROW, classes={"Plant": ""}, needs=["main_guard"]),
    Exercise("ex4", "ft_garden_security.py",
             ["Protected attributes, set_/get_height, set_/get_age.",
              "Negative values rejected with an error message."],
             GROW, classes={"Plant": ""}, functions=[
                 "set_height", "get_height", "set_age", "get_age"],
             needs=["protected"], forbid=["mangled"]),
    Exercise("ex5", "ft_plant_types.py",
             ["Flower, Tree, Vegetable inherit from Plant (super()).",
              "bloom(), produce_shade(), nutritional_value grows."],
             GROW | {"super"},
             classes={"Plant": "", "Flower": "Plant", "Tree": "Plant",
                      "Vegetable": "Plant"},
             functions=["bloom", "produce_shade"], needs=["super"]),
    Exercise("ex6", "ft_garden_analytics.py",
             ["Static & class methods, nested stats class, Seed(Flower).",
              "A function outside any class displays any plant's stats."],
             GROW | {"super", "staticmethod", "classmethod"},
             classes={"Plant": "", "Flower": "Plant", "Seed": "Flower",
                      "Tree": "Plant"},
             needs=["staticmethod", "classmethod", "nested_class", "super"]),
]

WORLD = World(
    id="w1",
    title="The Construct",
    project="Code Cultivation",
    subtitle="Object-oriented Python",
    mentor=MORPHEUS,
    intro=[
        Line(MORPHEUS, "I'm going to show you how deep the rabbit hole "
             "goes. Welcome to the Construct."),
        Line(MORPHEUS, "Here you'll learn what programs are made of: "
             "classes, objects, and the rules that bind them."),
    ],
    chapters=CHAPTERS,
    defense=[
        Riddle("Evaluator: 'Why use if __name__ == \"__main__\"?'",
               options=("It's faster",
                        "So the code under it runs when the file is "
                        "executed directly, but not when it's imported",
                        "Python requires it"),
               answer=1, explain="That's what makes a file reusable."),
        Riddle("Evaluator: 'What's the difference between a class and an "
               "instance?'",
               options=("None", "The class is the blueprint, an instance "
                        "is one object built from it with its own data",
                        "An instance is a function in a class"),
               answer=1, explain="Plant is the class, rose is an instance."),
        Riddle("Evaluator: 'Why protected attributes and setters?'",
               options=("To make the code longer",
                        "All changes go through methods that validate the "
                        "data, so it can't be corrupted",
                        "Python forbids public attributes"),
               answer=1, explain="That's encapsulation."),
        Riddle("Evaluator: 'How do you avoid duplicating code in Flower, "
               "Tree and Vegetable?'",
               options=("Copy-paste carefully",
                        "Put the common code in Plant, inherit from it, and"
                        " reuse it with super()",
                        "Use global variables"),
               answer=1, explain="Inheritance + super()."),
        Riddle("Evaluator: 'Static method or class method: which one "
               "creates the anonymous plant, and why?'",
               options=("A class method: it receives cls and can build "
                        "an instance of it",
                        "A static method: it receives self"),
               answer=0, explain="Static: no self/cls, a plain helper. "
                                 "Class method: gets cls, builds objects."),
    ],
    boss=Enemy("Agent Smith", art.AGENT,
               "Mr. Anderson... can you explain your own code?",
               "Smith's sunglasses crack. You explained every line."),
    exercises=EXERCISES,
    outro=[Line(MORPHEUS, "He is beginning to believe."),
           Line("Trinity", "Next stop: the Agents. They will throw "
                "everything at you.")],
)
