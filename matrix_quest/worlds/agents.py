"""World 2 - Agent Protocols: Garden Guardian (exception handling).

The trials use signals, hacks and the hardline instead of temperatures,
garden operations and the watering system.
"""

import ast

from ..forge import ForgeFailure, Spell, call, calls_named, lines, need, uses
from ..model import (Chapter, Check, Enemy, Exercise, Line, Page, Riddle, Run,
                     Trial, World)
from . import art

TRINITY = "Trinity"


# ============================================================ chapter 0

def _c0_valid(spell: Spell) -> None:
    result = call(need(spell, "read_signal"), "42")
    if result.error is not None:
        raise ForgeFailure(f"read_signal('42') raised {result.error!r}")
    if result.value != 42 or not isinstance(result.value, int):
        raise ForgeFailure(f"read_signal('42') returned {result.value!r}, "
                           "expected the integer 42")


def _c0_invalid(spell: Spell) -> None:
    result = call(need(spell, "read_signal"), "xyz")
    if not isinstance(result.error, ValueError):
        raise ForgeFailure(
            "read_signal('xyz') should let int() raise its ValueError, but "
            f"it gave {result.error or result.value!r}. (The catching "
            "happens in test_signal, not in read_signal!)")


def _c0_survives(spell: Spell) -> None:
    result = call(need(spell, "test_signal"))
    if result.error is not None:
        raise ForgeFailure(f"test_signal() crashed with {result.error!r}")
    if "42" not in result.output:
        raise ForgeFailure("test_signal() should print the valid signal")
    if "invalid literal" not in result.output:
        raise ForgeFailure("print the error message you caught (hint: "
                           "except ValueError as e: print(e))")


def _c0_try(spell: Spell) -> None:
    if not uses(spell, ast.Try):
        raise ForgeFailure("I don't see any try/except in your file.")


TRIAL_0 = Trial(
    id="w2c0",
    filename="w2_0_glitch.py",
    mission=[
        "The phone line carries signal strengths... and sometimes",
        "garbage. Write:",
        "",
        "  read_signal(signal_str: str) -> int",
        "      converts the text to an int and returns it.",
        "      It does NOT catch errors itself.",
        "",
        "  test_signal() -> None",
        "      tries read_signal('42') and read_signal('xyz'), prints the",
        "      result or the caught error, and finishes without crashing.",
        "",
        "Subject: ex0/ft_first_exception.py (input_temperature).",
    ],
    skeleton='''def read_signal(signal_str: str) -> int:
    # TODO: convert signal_str to an int and return it
    pass


def test_signal() -> None:
    print("=== Signal Check ===")
    # TODO: try read_signal("42") and print the result
    # TODO: try read_signal("xyz"), catch the error, print it
    # TODO: print a final message to prove the program didn't crash


if __name__ == "__main__":
    test_signal()
''',
    hints=[
        "int('42') gives 42; int('xyz') raises ValueError. read_signal "
        "needs one line.",
        "try: ... except ValueError as e: - e is the error object, print(e)"
        " shows its message.",
        "One try per test value, so the second test still runs after the "
        "first one failed.",
    ],
    checks=[
        ("read_signal('42') returns 42", _c0_valid),
        ("read_signal('xyz') lets ValueError escape", _c0_invalid),
        ("test_signal() survives and reports both", _c0_survives),
        ("try/except is used", _c0_try),
    ],
)


# ============================================================ chapter 1

def _c1_limits(spell: Spell) -> None:
    for text, number in (("42", 42), ("0", 0), ("100", 100)):
        result = call(need(spell, "read_signal"), text)
        if result.error is not None or result.value != number:
            raise ForgeFailure(f"read_signal({text!r}) should return "
                               f"{number} (limits included!) - got "
                               f"{result.value!r} / {result.error!r}")


def _c1_raises(text: str) -> Check:
    def check(spell: Spell) -> None:
        result = call(need(spell, "read_signal"), text)
        if not isinstance(result.error, ValueError):
            raise ForgeFailure(f"read_signal({text!r}) should raise a "
                               f"ValueError, got {result.error!r} / "
                               f"returned {result.value!r}")
        if text.lstrip("-").isdigit() and text not in str(result.error):
            raise ForgeFailure(f"the message should mention {text}: "
                               f"{str(result.error)!r}")
    return check


def _c1_survives(spell: Spell) -> None:
    result = call(need(spell, "test_signal"))
    if result.error is not None:
        raise ForgeFailure(f"test_signal() crashed with {result.error!r}")
    for value in ("42", "xyz", "150", "-7"):
        if value not in result.output:
            raise ForgeFailure(f"test_signal() should also test {value!r}")


def _c1_raise(spell: Spell) -> None:
    if not uses(spell, ast.Raise):
        raise ForgeFailure("you need the `raise` keyword somewhere!")


TRIAL_1 = Trial(
    id="w2c1",
    filename="w2_1_limits.py",
    mission=[
        "Agent Jones injects signals of 150% and -7%. Valid numbers -",
        "impossible signals. Upgrade your reader:",
        "",
        "  read_signal(signal_str: str) -> int",
        "      converts like before, then checks 0 <= signal <= 100.",
        "      Outside: raise ValueError with a message including the",
        "      number, e.g. '150 is too strong (max 100)'.",
        "",
        "  test_signal() -> None   tests '42', 'xyz', '150' and '-7'",
        "",
        "Subject: ex1/ft_raise_exception.py (0 to 40 degrees).",
    ],
    skeleton='''def read_signal(signal_str: str) -> int:
    signal = int(signal_str)
    # TODO: too strong -> raise ValueError(...)
    # TODO: too weak   -> raise ValueError(...)
    return signal


def test_signal() -> None:
    print("=== Signal Limits ===")
    # TODO: test "42", "xyz", "150" and "-7" (a loop keeps it short!)


if __name__ == "__main__":
    test_signal()
''',
    hints=[
        "raise ValueError('message') stops the function at once and sends "
        "the error to the caller.",
        "Build the message with an f-string: f'{signal} is too strong (max "
        "100)'.",
        "Limits included: 0 and 100 are fine. Test signal > 100 and "
        "signal < 0.",
    ],
    checks=[
        ("valid values (42, 0, 100) are returned", _c1_limits),
        ("'150' raises a ValueError mentioning 150", _c1_raises("150")),
        ("'-7' raises a ValueError mentioning -7", _c1_raises("-7")),
        ("'xyz' still raises ValueError", _c1_raises("xyz")),
        ("test_signal() tests all four values", _c1_survives),
        ("`raise` is used", _c1_raise),
    ],
)


# ============================================================ chapter 2

HEADS = (ValueError, ZeroDivisionError, FileNotFoundError, TypeError)


def _c2_head(number: int) -> Check:
    expected = HEADS[number]

    def check(spell: Spell) -> None:
        result = call(need(spell, "hack"), number)
        if not isinstance(result.error, expected):
            raise ForgeFailure(f"hack({number}) should raise "
                               f"{expected.__name__}, got {result.error!r}")
    return check


def _c2_calm(spell: Spell) -> None:
    for number in (4, 99, -1):
        result = call(need(spell, "hack"), number)
        if result.error is not None:
            raise ForgeFailure(f"hack({number}) should just return, but "
                               f"raised {result.error!r}")


def _c2_survives(spell: Spell) -> None:
    result = call(need(spell, "test_hacks"))
    if result.error is not None:
        raise ForgeFailure(f"test_hacks() crashed with {result.error!r}")
    for head in HEADS:
        if head.__name__ not in result.output:
            raise ForgeFailure(f"test_hacks() should report the "
                               f"{head.__name__} it caught")


def _c2_many(spell: Spell) -> None:
    for node in ast.walk(spell.tree):
        if isinstance(node, ast.Try) and len(node.handlers) >= 2:
            return
        if isinstance(node, ast.ExceptHandler) and \
                isinstance(node.type, ast.Tuple):
            return
    raise ForgeFailure("show one try: with several except clauses, or one "
                       "except (ErrorA, ErrorB):")


def _c2_no_type(spell: Spell) -> None:
    if calls_named(spell, "type"):
        raise ForgeFailure("type() is forbidden. Let each except clause "
                           "know which error it caught!")


TRIAL_2 = Trial(
    id="w2c2",
    filename="w2_2_twins.py",
    mission=[
        "The Twins phase through walls - each attack is a different",
        "error. Write:",
        "",
        "  hack(op_number: int) -> None",
        "      0 -> faulty code raising ValueError",
        "      1 -> faulty code raising ZeroDivisionError",
        "      2 -> faulty code raising FileNotFoundError",
        "      3 -> faulty code raising TypeError",
        "      anything else -> just return",
        "      Write REAL faulty code (int('abc'), 1 / 0...), not raise.",
        "",
        "  test_hacks() -> None",
        "      tries 0..4, catches each error by type, prints its name",
        "      and message. No type() allowed!",
        "",
        "Subject: ex2/ft_different_errors.py (garden_operations).",
    ],
    skeleton='''def hack(op_number: int) -> None:
    if op_number == 0:
        pass  # TODO: faulty code -> ValueError
    elif op_number == 1:
        pass  # TODO: faulty code -> ZeroDivisionError
    # TODO: 2 -> FileNotFoundError, 3 -> TypeError


def test_hacks() -> None:
    print("=== The Twins Attack ===")
    # TODO: for each op 0..4: try the hack, except each error type


if __name__ == "__main__":
    test_hacks()
''',
    hints=[
        "Faulty code: int('abc'), 10 / 0, open('/no/such/file'), "
        "'Neo' + 1.",
        "One try can have many except clauses; Python runs the FIRST one "
        "that matches.",
        "mypy complains about 'Neo' + 1: that's expected - keep it (or add "
        "# type: ignore).",
    ],
    checks=[
        ("hack(0) raises ValueError", _c2_head(0)),
        ("hack(1) raises ZeroDivisionError", _c2_head(1)),
        ("hack(2) raises FileNotFoundError", _c2_head(2)),
        ("hack(3) raises TypeError", _c2_head(3)),
        ("other numbers return calmly", _c2_calm),
        ("test_hacks() names every error and survives", _c2_survives),
        ("several error types caught by one try", _c2_many),
        ("no type() used", _c2_no_type),
    ],
)


# ============================================================ chapter 3

def _c3_family(spell: Spell) -> None:
    matrix = need(spell, "MatrixError")
    if not (isinstance(matrix, type) and issubclass(matrix, Exception)):
        raise ForgeFailure("MatrixError must inherit from Exception")
    agent, glitch = need(spell, "AgentError"), need(spell, "GlitchError")
    for cls in (agent, glitch):
        if not (isinstance(cls, type) and issubclass(cls, matrix)):
            raise ForgeFailure(f"{cls!r} must inherit from MatrixError")
    if issubclass(agent, glitch) or issubclass(glitch, agent):
        raise ForgeFailure("AgentError and GlitchError are siblings")


def _c3_defaults(spell: Spell) -> None:
    for name in ("MatrixError", "AgentError", "GlitchError"):
        result = call(need(spell, name))
        if result.error is not None:
            raise ForgeFailure(f"{name}() crashed: {result.error!r}")
        if str(result.value) == "":
            raise ForgeFailure(f"str({name}()) is empty - give it a default"
                               " message")


def _c3_custom(spell: Spell) -> None:
    text = "An Agent is coming!"
    for name in ("AgentError", "GlitchError"):
        result = call(need(spell, name), text)
        if result.error is not None or str(result.value) != text:
            raise ForgeFailure(f"{name}({text!r}) should keep that message")


def _c3_raisers(spell: Spell) -> None:
    for function, cls in (("summon_agent", "AgentError"),
                          ("cause_glitch", "GlitchError")):
        result = call(need(spell, function))
        if not isinstance(result.error, need(spell, cls)):
            raise ForgeFailure(f"{function}() should raise {cls}, got "
                               f"{result.error!r}")


def _c3_survives(spell: Spell) -> None:
    result = call(need(spell, "test_matrix_errors"))
    if result.error is not None:
        raise ForgeFailure(f"test_matrix_errors() crashed: "
                           f"{result.error!r}")
    for word in ("AgentError", "GlitchError", "MatrixError"):
        if word not in result.output:
            raise ForgeFailure(f"the output should show a caught {word}")


TRIAL_3 = Trial(
    id="w2c3",
    filename="w2_3_exiles.py",
    mission=[
        "Python's errors don't know about Agents or glitches. Create",
        "your own:",
        "",
        "  class MatrixError(Exception)    default 'Unknown Matrix error'",
        "  class AgentError(MatrixError)   default 'Unknown agent error'",
        "  class GlitchError(MatrixError)  default 'Unknown glitch error'",
        "",
        "  summon_agent() -> None   raises AgentError('Agent Smith is here!')",
        "  cause_glitch() -> None   raises GlitchError('Deja vu...')",
        "",
        "  test_matrix_errors() -> None",
        "      catches AgentError, then GlitchError, then shows that",
        "      except MatrixError catches BOTH.",
        "",
        "Subject: ex3/ft_custom_errors.py (GardenError, PlantError...).",
    ],
    skeleton='''class MatrixError(Exception):
    # TODO: give it a default message
    pass


# TODO: class AgentError(...)
# TODO: class GlitchError(...)


def summon_agent() -> None:
    pass  # TODO: raise an AgentError


def cause_glitch() -> None:
    pass  # TODO: raise a GlitchError


def test_matrix_errors() -> None:
    print("=== Custom Matrix Errors ===")
    # TODO


if __name__ == "__main__":
    test_matrix_errors()
''',
    hints=[
        "class AgentError(MatrixError): means every AgentError IS ALSO a "
        "MatrixError.",
        "Default message: def __init__(self, message: str = 'Unknown agent "
        "error') -> None:  super().__init__(message)",
        "except MatrixError catches all its children. Loop over "
        "[summon_agent, cause_glitch] and call each inside one try.",
    ],
    checks=[
        ("the error family tree is right", _c3_family),
        ("each error has a default message", _c3_defaults),
        ("a custom message is kept", _c3_custom),
        ("summon_agent/cause_glitch raise the right error", _c3_raisers),
        ("test_matrix_errors() catches them all", _c3_survives),
    ],
)


# ============================================================ chapter 4

def _c4_jack(spell: Spell) -> None:
    need(spell, "GlitchError")
    result = call(need(spell, "jack_in"), "Trinity")
    if result.error is not None:
        raise ForgeFailure(f"jack_in('Trinity') raised {result.error!r}")
    if "Trinity" not in result.output:
        raise ForgeFailure("jack_in('Trinity') should print a success "
                           "message with the name")


def _c4_bad(spell: Spell) -> None:
    result = call(need(spell, "jack_in"), "cypher")
    if not isinstance(result.error, need(spell, "GlitchError")):
        raise ForgeFailure(f"jack_in('cypher') should raise GlitchError, "
                           f"got {result.error!r}")
    if "cypher" not in str(result.error):
        raise ForgeFailure("the error message should contain the bad name")


def _c4_mission(crew: list[str], stop: str) -> Check:
    def check(spell: Spell) -> None:
        result = call(need(spell, "run_mission"), crew)
        if result.error is not None:
            raise ForgeFailure(f"run_mission({crew}) let an error escape: "
                               f"{result.error!r}")
        found = lines(result.output)
        if not found or "open" not in found[0].lower():
            raise ForgeFailure("the first line should open the hardline")
        if "clos" not in found[-1].lower():
            raise ForgeFailure("the LAST line should close the hardline")
        closes = [line for line in found if "clos" in line.lower()]
        if len(closes) != 1:
            raise ForgeFailure(f"the hardline closed {len(closes)} times! "
                               "Close it once, only in finally.")
        if stop and stop in result.output:
            raise ForgeFailure(f"after the error, {stop!r} must not jack "
                               "in: stop and return immediately")
    return check


def _c4_finally(spell: Spell) -> None:
    if not any(isinstance(node, ast.Try) and node.finalbody
               for node in ast.walk(spell.tree)):
        raise ForgeFailure("I don't see a finally: block")


TRIAL_4 = Trial(
    id="w2c4",
    filename="w2_4_hardline.py",
    mission=[
        "Whatever happens, the hardline must be closed - or the Agents",
        "trace the call.",
        "",
        "  class GlitchError(Exception)  (from 'Programs in Exile')",
        "  jack_in(name: str) -> None",
        "      capitalized ('Trinity'): print a success message",
        "      otherwise ('cypher'):    raise GlitchError with the name",
        "  run_mission(crew: list[str]) -> None",
        "      print 'Opening the hardline', jack in each member.",
        "      On GlitchError: print it, then return immediately.",
        "      finally: print 'Closing the hardline'.",
        "  test_hardline() -> None   a good crew, then a bad one",
        "",
        "Subject: ex4/ft_finally_block.py (water_plant).",
    ],
    skeleton='''class GlitchError(Exception):
    pass  # TODO: your GlitchError from 'Programs in Exile'


def jack_in(name: str) -> None:
    pass  # TODO


def run_mission(crew: list[str]) -> None:
    print("Opening the hardline")
    # TODO: try / except GlitchError / finally


def test_hardline() -> None:
    print("=== The Hardline ===")
    run_mission(["Neo", "Trinity", "Morpheus"])
    print()
    run_mission(["Neo", "cypher", "Trinity"])


if __name__ == "__main__":
    test_hardline()
''',
    hints=[
        "'cypher'.capitalize() is 'Cypher'. A name is OK when it equals its"
        " capitalized version.",
        "Put the whole for loop inside the try: the first GlitchError jumps"
        " out of the loop to the except.",
        "return inside except STILL runs finally. Print the closing line "
        "only there.",
    ],
    checks=[
        ("jack_in('Trinity') succeeds", _c4_jack),
        ("jack_in('cypher') raises GlitchError", _c4_bad),
        ("good crew: open, jack in, close once",
         _c4_mission(["Neo", "Trinity"], "")),
        ("bad crew: stops at 'cypher' but still closes",
         _c4_mission(["Neo", "cypher", "Trinity"], "Trinity")),
        ("finally is used", _c4_finally),
    ],
)

# ============================================================ the story

CHAPTERS = [
    Chapter(
        id="w2c0",
        title="A Glitch in the Matrix",
        exercise="ex0 · ft_first_exception.py",
        concept="try / except · catching errors",
        story=[
            Line("Neo", "Whoa. Déjà vu."),
            Line(TRINITY, "What did you just see?"),
            Line("Neo", "A black cat went past us... and then another that "
                 "looked just like it."),
            Line(TRINITY, "A glitch. When the Matrix meets something "
                 "impossible, it raises an alarm. If nobody catches it, "
                 "everything crashes."),
        ],
        pages=[
            Page("Exceptions", [
                "When Python meets something impossible, it RAISES an "
                "exception: an object describing what went wrong.",
                "Uncaught, it stops the program and prints a Traceback: a "
                "crash. The subjects say: your programs must never crash.",
            ], 'signal = int("abc")   # ValueError!\nprint("never reached")'),
            Page("try / except", [
                "try: draws a safety net. If an exception is raised inside,"
                " Python jumps to the matching except, skipping the rest of"
                " the try - then carries on after it.",
            ], 'try:\n'
               '    signal = int("abc")\n'
               '    print("skipped")\n'
               'except ValueError as e:\n'
               '    print("Caught:", e)\n'
               'print("Still alive!")'),
            Page("Errors travel up", [
                "If int() fails inside read_signal(), the error flies OUT "
                "of read_signal() to whoever called it. So the function "
                "just converts, and the test catches.",
                "as e names the error: print(e) shows its message.",
            ], 'def read_signal(text: str) -> int:\n'
               '    return int(text)          # may raise\n'
               '\n'
               '\n'
               'try:\n'
               '    read_signal("abc")        # the error arrives here\n'
               'except ValueError as e:      # and is caught here\n'
               '    print("Caught:", e)'),
        ],
        enemy=Enemy("the Déjà Vu Cat", art.CAT,
                    "Mrrrow. Mrrrow. (It walks past you. Twice.)",
                    "The glitch is caught. The Matrix keeps running."),
        riddles=[
            Riddle("What does this print?",
                   code='try:\n    x = int("abc")\n    print("A")\n'
                        'except ValueError:\n    print("B")\nprint("C")',
                   options=("A B C", "B C", "A C", "It crashes"),
                   answer=1, run=True,
                   explain="int('abc') raises, so print('A') is skipped."),
            Riddle("Fill the blank:   ______ ValueError as e:",
                   kind="blank", answer=("except",),
                   explain="except catches; as e names the error."),
            Riddle("What does this print?",
                   code='try:\n    int("hello")\n'
                        'except ValueError as e:\n    print(e)',
                   options=("hello", "invalid literal for int() with base "
                            "10: 'hello'", "ValueError"),
                   answer=1, run=True,
                   explain="print(e) shows the MESSAGE of the exception."),
            Riddle("And WITHOUT try/except?",
                   code='print(int("abc"))\nprint("done")',
                   options=("It prints done",
                            "It crashes: 'done' is never printed"),
                   answer=1, run=True,
                   explain="An uncaught exception stops everything."),
            Riddle("test_signal() calls read_signal('abc') inside a try. "
                   "Where is the ValueError caught?",
                   options=("Nowhere, it crashes",
                            "Inside int(), automatically",
                            "It travels up out of read_signal() into the "
                            "except of test_signal()"),
                   answer=2,
                   explain="Exceptions climb up the callers until someone "
                           "catches them."),
        ],
        trial=TRIAL_0,
        victory=[Line(TRINITY, "Glitches still happen. But now they don't "
                      "crash anything.")],
    ),
    Chapter(
        id="w2c1",
        title="Agent Jones's Limits",
        exercise="ex1 · ft_raise_exception.py",
        concept="raise · validating values",
        story=[
            Line("Tank", "Signal at 150%! Now -7%! Those are numbers... but"
                 " impossible ones."),
            Line(TRINITY, "Agent Jones is feeding us fake readings."),
            Line(TRINITY, "Catching errors isn't enough, Neo. Sometimes YOU"
                 " must sound the alarm. Raise it."),
        ],
        pages=[
            Page("raise", [
                "raise creates an exception yourself, when the data is "
                "fine for Python but wrong for YOUR program: 100°C is a "
                "valid int, yet plants would cook.",
                "raise stops the function at once - like return, but for "
                "bad news.",
            ], 'def read_temperature(text: str) -> int:\n'
               '    temperature = int(text)\n'
               '    if temperature > 40:\n'
               '        raise ValueError(f"{temperature}°C is too hot")\n'
               '    return temperature'),
            Page("Why not return -1?", [
                "-1 could be a real value! An exception can't be mistaken "
                "for data, and can't be silently ignored.",
                "'0 to 40, limits included' means 0 and 40 are VALID.",
            ]),
        ],
        enemy=Enemy("Agent Jones", art.AGENT,
                    "150 percent. Minus seven. Perfectly valid integers.",
                    "Your raise statements stop every fake reading."),
        riddles=[
            Riddle("What does this print?",
                   code='def check(t: int) -> int:\n'
                        '    if t > 40:\n'
                        '        raise ValueError(f"{t} is too hot")\n'
                        '    print("checked")\n'
                        '    return t\n\n\n'
                        'try:\n    check(100)\n'
                        'except ValueError as e:\n    print("Caught:", e)',
                   options=("checked / Caught: 100 is too hot",
                            "Caught: 100 is too hot", "checked"),
                   answer=1, run=True,
                   explain="raise leaves the function: no 'checked'."),
            Riddle("Fill the blank:   ______ ValueError('too weak')",
                   kind="blank", answer=("raise",),
                   explain="raise throws the exception."),
            Riddle("0 to 40, limits included. Which test finds BAD values?",
                   options=("t < 0 or t > 40", "t <= 0 or t >= 40",
                            "t < 0 and t > 40"),
                   answer=0,
                   explain="0 and 40 are allowed. ('and' is never true!)"),
            Riddle("What does int(\"-50\") do?",
                   code='print(int("-50"))',
                   options=("ValueError", "returns -50"),
                   answer=1, run=True,
                   explain="Python accepts -50: only YOUR check can refuse "
                           "it."),
            Riddle("What does this print?",
                   code='for text in ["25", "abc", "100"]:\n'
                        '    try:\n'
                        '        t = int(text)\n'
                        '        if t > 40:\n'
                        '            raise ValueError(f"{t} too hot")\n'
                        '        print("ok", t)\n'
                        '    except ValueError as e:\n'
                        '        print("error:", e)',
                   options=("ok 25 / error: invalid literal... / error: "
                            "100 too hot", "ok 25 / then a crash"),
                   answer=0, run=True,
                   explain="Python's ValueError and yours are the same "
                           "type: one except handles both."),
        ],
        trial=TRIAL_1,
        victory=[Line("Tank", "Fake readings rejected. Agent Jones is "
                      "furious.")],
    ),
    Chapter(
        id="w2c2",
        title="The Twins",
        exercise="ex2 · ft_different_errors.py",
        concept="error types · several except clauses",
        story=[
            Line("Morpheus", "The Merovingian's twins. They phase through "
                 "walls, and each attack is different."),
            Line(TRINITY, "One shield won't do. Learn the NAME of each "
                 "attack, and you can block them all."),
        ],
        pages=[
            Page("Many types of errors", [
                "ValueError: bad value - int('abc')",
                "ZeroDivisionError: dividing by zero - 10 / 0",
                "FileNotFoundError: missing file - open('/nope')",
                "TypeError: mixing types - 'Neo' + 1",
                "...and KeyError, IndexError, AttributeError and more.",
            ]),
            Page("Several except clauses", [
                "Python checks the clauses from top to bottom and runs "
                "only the FIRST that matches. Each clause knows what it "
                "caught: no need for type() (forbidden in the subject).",
                "A tuple catches several types in one clause.",
            ], 'try:\n'
               '    hack(op)\n'
               'except ValueError as e:\n'
               '    print(f"Caught ValueError: {e}")\n'
               'except (ZeroDivisionError, TypeError) as e:\n'
               '    print("Caught a math or type error:", e)'),
            Page("The family tree of exceptions", [
                "Exception > ArithmeticError > ZeroDivisionError",
                "Exception > OSError > FileNotFoundError",
                "except Exception catches (almost) everything - so always "
                "put SPECIFIC errors before general ones.",
            ]),
        ],
        enemy=Enemy("the Twins", art.TWINS,
                    "We are getting aggravated. Yes, we are.",
                    "Each attack meets the right except. The Twins fade."),
        riddles=[
            Riddle("Which exception does 10 / 0 raise?", code="10 / 0",
                   options=("ValueError", "ZeroDivisionError", "TypeError"),
                   answer=1, run=True, explain="Dividing by zero."),
            Riddle("Which exception does this raise?", code='"Neo" + 1',
                   options=("ValueError", "TypeError", "'Neo1'"),
                   answer=1, run=True, explain="str + int can't mix."),
            Riddle("Which exception does this raise?",
                   code='open("/non/existent/file")',
                   options=("FileNotFoundError", "KeyError",
                            "Nothing, it creates the file"),
                   answer=0, run=True,
                   explain="Reading a missing file. It never opened, so "
                           "there's nothing to close()."),
            Riddle("A trap! What does this print?",
                   code='try:\n    int("abc")\nexcept Exception:\n'
                        '    print("general")\nexcept ValueError:\n'
                        '    print("specific")',
                   options=("specific", "general", "general / specific"),
                   answer=1, run=True,
                   explain="ValueError IS an Exception: the first clause "
                           "matches. Specific first!"),
            Riddle("What happens here?",
                   code='for op in [0, 1, 2]:\n    try:\n'
                        '        if op == 0:\n            int("abc")\n'
                        '        elif op == 1:\n            1 / 0\n'
                        '        else:\n            [1, 2][5]\n'
                        '    except (ValueError, ZeroDivisionError) as e:\n'
                        '        print("caught:", e)',
                   options=("Three 'caught' lines",
                            "Two 'caught' lines, then a crash (IndexError)"),
                   answer=1, run=True,
                   explain="Only the listed types are caught."),
        ],
        trial=TRIAL_2,
        victory=[Line("Morpheus", "Every attack, named and blocked.")],
    ),
    Chapter(
        id="w2c3",
        title="Programs in Exile",
        exercise="ex3 · ft_custom_errors.py",
        concept="custom exception classes · inheritance",
        story=[
            Line("The Merovingian", "Ah, programs in exile. Rogue "
                 "programs. Python has no name for us, non?"),
            Line(TRINITY, "Then we'll give them names. Errors of our own "
                 "world: MatrixError, AgentError, GlitchError."),
        ],
        pages=[
            Page("Your own exception types", [
                "An exception type is just a class inheriting from "
                "Exception. Two lines!",
            ], 'class MatrixError(Exception):\n    pass\n\n\n'
               'raise MatrixError("Something is wrong in the Matrix")'),
            Page("A family of errors", [
                "AgentError(MatrixError) means every AgentError IS a "
                "MatrixError, so except MatrixError catches all children.",
                "By default str(MatrixError()) is empty: add a default "
                "message with __init__ and super().",
            ], 'class AgentError(MatrixError):\n'
               '    def __init__(self, message: str = "Unknown agent '
               'error") -> None:\n'
               '        super().__init__(message)'),
        ],
        enemy=Enemy("the Merovingian", art.AGENT,
                    "Choice is an illusion. And so are your built-in "
                    "errors.",
                    "Every rogue program now has a name. The Merovingian "
                    "shrugs."),
        riddles=[
            Riddle("What does this print?",
                   code='class MatrixError(Exception):\n    pass\n\n\n'
                        'class AgentError(MatrixError):\n    pass\n\n\n'
                        'try:\n    raise AgentError("Smith!")\n'
                        'except MatrixError as e:\n    print("Caught:", e)',
                   options=("Caught: Smith!", "It crashes"),
                   answer=0, run=True,
                   explain="A parent's except catches its children."),
            Riddle("The other way around?",
                   code='class MatrixError(Exception):\n    pass\n\n\n'
                        'class AgentError(MatrixError):\n    pass\n\n\n'
                        'try:\n    raise MatrixError("glitch")\n'
                        'except AgentError as e:\n    print("Caught:", e)',
                   options=("Caught: glitch", "It crashes"),
                   answer=1, run=True,
                   explain="A MatrixError is not necessarily an AgentError."),
            Riddle("What does this print?",
                   code='class GlitchError(Exception):\n    pass\n\n\n'
                        'print("[" + str(GlitchError()) + "]")',
                   options=("[GlitchError]", "[]"),
                   answer=1, run=True,
                   explain="No message = empty text. Hence the default."),
            Riddle("Fill the blank:   class AgentError(___________):",
                   kind="blank", answer=("MatrixError",),
                   explain="The parent goes in the parentheses."),
        ],
        trial=TRIAL_3,
        victory=[Line(TRINITY, "Now our errors speak our language.")],
    ),
    Chapter(
        id="w2c4",
        title="The Hardline",
        exercise="ex4 · ft_finally_block.py",
        concept="finally · cleanup that always runs",
        story=[
            Line("Tank", "Operator. You need an exit, Neo: the hardline at "
                 "the old phone booth."),
            Line(TRINITY, "Whatever happens - an Agent, a glitch, a return"
                 " - the line must be closed. Or they trace us."),
            Line(TRINITY, "There's one spell that ALWAYS runs: finally."),
        ],
        pages=[
            Page("finally always runs", [
                "After the try, whatever happened: no error, a caught "
                "error, an uncaught error, a return - finally runs.",
            ], 'try:\n'
               '    print("Opening the hardline")\n'
               '    jack_in("cypher")       # may raise\n'
               'except GlitchError as e:\n'
               '    print("Caught:", e)\n'
               'finally:\n'
               '    print("Closing the hardline")'),
            Page("Cleanup belongs in finally", [
                "Closing files, connections, phone lines... Put the "
                "closing line ONLY in finally: in except too, it would run"
                " twice.",
                "return inside except leaves the function, and finally "
                "still runs on the way out.",
            ]),
        ],
        enemy=Enemy("the Sentinel Swarm", art.SENTINEL,
                    "*screeching* (they follow any line left open)",
                    "The line clicks shut in its finally. The swarm loses "
                    "the trace."),
        riddles=[
            Riddle("What does this print?",
                   code='try:\n    print("open")\n    int("abc")\n'
                        '    print("work")\nexcept ValueError:\n'
                        '    print("error")\nfinally:\n    print("close")',
                   options=("open / work / close", "open / error / close",
                            "open / error"),
                   answer=1, run=True, explain="Error, except, finally."),
            Riddle("With a return inside except?",
                   code='def call() -> None:\n    try:\n'
                        '        print("open")\n'
                        '        raise ValueError("bad")\n'
                        '    except ValueError:\n'
                        '        print("caught")\n        return\n'
                        '    finally:\n        print("close")\n'
                        '    print("after")\n\n\ncall()',
                   options=("open / caught", "open / caught / close",
                            "open / caught / close / after"),
                   answer=1, run=True,
                   explain="finally runs on the way out; 'after' never."),
            Riddle("With an error NOBODY catches?",
                   code='try:\n    print("open")\n    1 / 0\n'
                        'finally:\n    print("close")',
                   options=("open, then a crash",
                            "open / close, then a crash"),
                   answer=1, run=True,
                   explain="finally runs - but doesn't CATCH anything."),
            Riddle("Fill the blank:   ________:  print('Closing')  "
                   "(must run no matter what)",
                   kind="blank", answer=("finally",),
                   explain="finally = always."),
        ],
        trial=TRIAL_4,
        victory=[Line("Tank", "Line closed. Untraceable. Welcome back, "
                      "Neo.")],
    ),
]

EXERCISES = [
    Exercise("ex0", "ft_first_exception.py",
             ["input_temperature(temp_str) converts and returns an int.",
              "test_temperature() tries '25' and 'abc' and survives."],
             {"int", "print"},
             functions=["input_temperature", "test_temperature"],
             needs=["try"],
             runs=[Run(expect=["25", "abc", "invalid literal"])]),
    Exercise("ex1", "ft_raise_exception.py",
             ["Like ex0, plus: raise if not 0..40 (limits included).",
              "Also test '100' and '-50'."],
             {"int", "print"},
             functions=["input_temperature", "test_temperature"],
             needs=["try", "raise"],
             runs=[Run(expect=["25", "abc", "100", "-50"])]),
    Exercise("ex2", "ft_different_errors.py",
             ["garden_operations(n): 0..3 raise Value/ZeroDivision/"
              "FileNotFound/TypeError.",
              "test_error_types() catches each one, without type()."],
             {"print", "open", "int"},
             functions=["garden_operations", "test_error_types"],
             needs=["try"], forbid=["type()"],
             runs=[Run(expect=["ValueError", "ZeroDivisionError",
                               "FileNotFoundError", "TypeError"])]),
    Exercise("ex3", "ft_custom_errors.py",
             ["GardenError(Exception), PlantError and WaterError, with "
              "default messages.",
              "Raise them, catch them, catch all with GardenError."],
             {"print"},
             classes={"GardenError": "Exception",
                      "PlantError": "GardenError",
                      "WaterError": "GardenError"},
             needs=["try", "raise"],
             runs=[Run(expect=["PlantError", "WaterError", "GardenError"])]),
    Exercise("ex4", "ft_finally_block.py",
             ["water_plant(name): OK if capitalized, else PlantError.",
              "test_watering_system(): stop at first error, close in "
              "finally."],
             {"print", "capitalize"},
             functions=["water_plant", "test_watering_system"],
             classes={"PlantError": ""}, needs=["try", "raise", "finally"],
             runs=[Run(expect=["Opening", "Closing", "PlantError"])]),
]

WORLD = World(
    id="w2",
    title="Agent Protocols",
    project="Garden Guardian",
    subtitle="Exception handling",
    mentor=TRINITY,
    intro=[
        Line(TRINITY, "Out there, Agents will throw everything at you. "
             "Bad data. Impossible values. Missing files."),
        Line(TRINITY, "A real hacker's programs don't crash. They catch, "
             "they raise, they always clean up."),
    ],
    chapters=CHAPTERS,
    defense=[
        Riddle("Evaluator: 'Why does Python have different error types?'",
               options=("To look complicated",
                        "So each problem can be recognised and handled in "
                        "its own way"),
               answer=1, explain="A missing file is not bad data."),
        Riddle("Evaluator: 'Why doesn't input_temperature() catch its own "
               "error?'",
               options=("It's a bug",
                        "It only converts; the caller decides what to do "
                        "with a failure, so the error travels up"),
               answer=1, explain="Raise where you detect, catch where you "
                                 "can act."),
        Riddle("Evaluator: 'How do you catch several types with one try:?'",
               options=("Several except clauses, or a tuple like "
                        "(ValueError, TypeError)",
                        "type(e) in an if", "One try per type"),
               answer=0, explain="And type() is forbidden anyway."),
        Riddle("Evaluator: 'Why clean up in finally and not after the try?'",
               options=("finally is faster",
                        "An error or a return could skip the code after the"
                        " try; finally runs no matter what"),
               answer=1, explain="That's the point of finally."),
    ],
    boss=Enemy("Agent Smith (upgraded)", art.CROWD,
               "Why, Mr. Anderson? Why do you persist? Your code will "
               "crash.",
               "Not one crash. Smith has nothing left to throw."),
    exercises=EXERCISES,
    outro=[Line(TRINITY, "You don't crash anymore, Neo."),
           Line("Morpheus", "Now the Oracle wants to see you.")],
)
