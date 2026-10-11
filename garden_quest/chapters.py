"""The story: five chapters, one per exercise, and the final trial."""

from dataclasses import dataclass

from .battle import Monster, Riddle
from .forge import ForgeTrial
from .trials import TRIAL_0, TRIAL_1, TRIAL_2, TRIAL_3, TRIAL_4


@dataclass
class Page:
    """One page of the Spellbook: some text and an example."""
    text: list[str]
    code: str = ""


@dataclass
class Chapter:
    number: int
    title: str
    exercise: str
    rune: str
    story: list[str]
    pages: list[Page]
    monster: Monster
    riddles: list[Riddle]
    trial: ForgeTrial
    victory: list[str]


# ================================================================ chapter 0

CHAPTER_0 = Chapter(
    number=0,
    title="The Whispering Thermometer",
    exercise="Exercise 0 - ft_first_exception.py (try / except)",
    rune="🌱 Rune of Catching (try/except)",
    story=[
        "The Enchanted Greenhouse of Codehaven is dying.",
        "Its magical sensors used to sing the temperature to the plants,",
        "but the Chaos Blight has crept into the wires. Now the sensors",
        "sometimes whisper nonsense: 'abc', '#!?', 'banana'...",
        "Every time a sensor says nonsense, the old greenhouse program",
        "CRASHES - and the sprinklers, lamps and heaters all go dark.",
        "The Elder Gardener hands you a dusty Grimoire. 'Learn to catch",
        "the Blight before it breaks the program, young Guardian.'",
    ],
    pages=[
        Page([
            "When Python meets something impossible, it RAISES an",
            "exception: an object that describes what went wrong.",
            "If nobody catches it, the program stops and prints a",
            "Traceback. That is a crash - the thing we must never allow.",
        ], 'temperature = int("abc")   # ValueError!\n'
           'print("never reached")'),
        Page([
            "A `try:` block is a protective circle. If an exception is",
            "raised inside it, Python jumps straight to the matching",
            "`except` block. The rest of the try block is skipped, and the",
            "program carries on after the except - no crash!",
        ], 'try:\n'
           '    temperature = int("abc")\n'
           '    print("skipped")\n'
           'except ValueError as e:\n'
           '    print("Caught an error:", e)\n'
           'print("Still alive!")'),
        Page([
            "`as e` gives the exception a name. print(e) shows its",
            "message, e.g.  invalid literal for int() with base 10: 'abc'.",
            "",
            "Errors TRAVEL: if int() fails inside input_temperature(),",
            "the error flies out of input_temperature() up to whoever",
            "called it. So input_temperature() just converts, and",
            "test_temperature() is the one who catches.",
        ], 'def input_temperature(temp_str: str) -> int:\n'
           '    return int(temp_str)        # may raise ValueError\n'
           '\n'
           'try:\n'
           '    input_temperature("abc")    # the error arrives here...\n'
           'except ValueError as e:        # ...and is caught here\n'
           '    print("Caught:", e)'),
    ],
    monster=Monster(
        name="the Garbled Gremlin",
        art=r"""
              .-""-.
             / x  x \      *chitter* abc! #?! b4n4n4!
            |  .--.  |
             \ '--' /
          ~~~/`----'\~~~
""",
        taunt="I'll feed your sensors nonsense until your program crashes!",
        defeat="The Garbled Gremlin bursts into harmless letters. "
               "The thermometer sings '25°C' again!",
    ),
    riddles=[
        Riddle(
            question="What does int(\"25\") give back?",
            options=('the text "25"', "the integer 25", "a ValueError",
                     "None"),
            answer=1,
            explain="int() converts a text that looks like a whole number "
                    "into a real int you can do maths with.",
        ),
        Riddle(
            question="What does this print?",
            code='try:\n'
                 '    x = int("abc")\n'
                 '    print("A")\n'
                 'except ValueError:\n'
                 '    print("B")\n'
                 'print("C")',
            options=("A B C", "B C", "A C", "It crashes"),
            answer=1,
            run=True,
            explain="int('abc') raises, so print('A') is SKIPPED. Python "
                    "jumps to except (B) and then continues normally (C).",
        ),
        Riddle(
            question="Fill the blank:   ______ ValueError as e:",
            kind="blank",
            answer=("except",),
            explain="`except SomeError as e:` catches that error and names "
                    "it `e`.",
        ),
        Riddle(
            question="What does this print?",
            code='try:\n'
                 '    int("hello")\n'
                 'except ValueError as e:\n'
                 '    print(e)',
            options=("hello", "invalid literal for int() with base 10: "
                     "'hello'", "ValueError", "Nothing"),
            answer=1,
            run=True,
            explain="print(e) shows the exception's MESSAGE. This is the "
                    "exact text the subject's example output shows.",
        ),
        Riddle(
            question="And WITHOUT try/except?",
            code='print(int("abc"))\nprint("done")',
            options=("It prints done", "It crashes: 'done' is never printed",
                     "It prints None, then done"),
            answer=1,
            run=True,
            explain="An uncaught exception stops the whole program. The "
                    "subject says: your programs must never crash.",
        ),
        Riddle(
            question="test_temperature() calls input_temperature('abc') "
                     "inside a try. Where is the ValueError caught?",
            options=("Nowhere, it crashes",
                     "Inside int(), automatically",
                     "It travels up out of input_temperature() and is "
                     "caught by the except in test_temperature()"),
            answer=2,
            explain="Exceptions climb up the chain of callers until "
                    "someone catches them. That's why input_temperature "
                    "can stay simple.",
        ),
    ],
    trial=TRIAL_0,
    victory=[
        "The sensors still whisper nonsense now and then...",
        "but the greenhouse program no longer crashes. It simply notes",
        "the bad reading and keeps the lamps glowing.",
    ],
)


# ================================================================ chapter 1

CHAPTER_1 = Chapter(
    number=1,
    title="The Ember Drake",
    exercise="Exercise 1 - ft_raise_exception.py (raise)",
    rune="🔥 Rune of Raising (raise)",
    story=[
        "A deep rumble shakes the greenhouse. The thermometer reads 100°C!",
        "Then -50°C! The numbers are VALID numbers... but no plant can",
        "live in that. The Ember Drake, napping beneath the soil, is",
        "toying with the sensors.",
        "'Catching errors is not enough,' says the Elder Gardener.",
        "'Sometimes YOU must sound the alarm. You must learn to RAISE.'",
    ],
    pages=[
        Page([
            "`raise` creates an exception yourself. Use it when the data",
            "is technically fine for Python but wrong for YOUR program:",
            "100°C is a perfect int, yet plants would cook.",
        ], 'raise ValueError("100°C is too hot for plants (max 40°C)")'),
        Page([
            "raise stops the function immediately - like return, but for",
            "bad news. The exception then travels to the caller's except.",
            "Build messages with f-strings to include the value.",
        ], 'def input_temperature(temp_str: str) -> int:\n'
           '    temp = int(temp_str)\n'
           '    if temp > 40:\n'
           '        raise ValueError(f"{temp}°C is too hot")\n'
           '    return temp            # only reached if all is well'),
        Page([
            "Why not just return -1 for bad values? Because -1 could be a",
            "real temperature! An exception can't be mistaken for data,",
            "and it can't be ignored silently: someone must handle it.",
            "",
            "'0 to 40, limits included' means 0 and 40 are VALID.",
        ]),
    ],
    monster=Monster(
        name="the Ember Drake",
        art=r"""
                    __====-_  _-====__
              _--^^^#####//      \\#####^^^--_
           _-^##########// (    ) \\##########^-_
          -############//  |\^^/|  \\############-
                         ( 100°C )
""",
        taunt="100 degrees! Minus 50! Perfectly valid numbers, hahaha!",
        defeat="The Ember Drake hits your wall of `raise` and slinks "
               "back underground, grumbling about 'limits included'.",
    ),
    riddles=[
        Riddle(
            question="What does this print?",
            code='def check(t: int) -> int:\n'
                 '    if t > 40:\n'
                 '        raise ValueError(f"{t}°C is too hot")\n'
                 '    print("checked")\n'
                 '    return t\n'
                 '\n'
                 'try:\n'
                 '    check(100)\n'
                 'except ValueError as e:\n'
                 '    print("Caught:", e)',
            options=("checked, then Caught: 100°C is too hot",
                     "Caught: 100°C is too hot",
                     "checked", "It crashes"),
            answer=1,
            run=True,
            explain="raise leaves the function at once, so 'checked' is "
                    "never printed.",
        ),
        Riddle(
            question="Fill the blank:   ______ ValueError('too cold')",
            kind="blank",
            answer=("raise",),
            explain="`raise` throws the exception.",
        ),
        Riddle(
            question="Plants accept 0 to 40, limits included. Which test "
                     "finds the BAD temperatures?",
            options=("t < 0 or t > 40", "t <= 0 or t >= 40",
                     "t < 0 and t > 40", "0 < t < 40"),
            answer=0,
            explain="0 and 40 are allowed, so only strictly below 0 or "
                    "strictly above 40 is bad. ('and' can never be true!)",
        ),
        Riddle(
            question="What does int(\"-50\") do?",
            code='print(int("-50"))',
            options=("ValueError, negative numbers aren't allowed",
                     "returns -50", "returns 50"),
            answer=1,
            run=True,
            explain="Python is happy with -50. Only YOUR range check can "
                    "catch it - that's why you need raise.",
        ),
        Riddle(
            question="What does this print?",
            code='for text in ["25", "abc", "100"]:\n'
                 '    try:\n'
                 '        t = int(text)\n'
                 '        if t > 40:\n'
                 '            raise ValueError(f"{t} too hot")\n'
                 '        print("ok", t)\n'
                 '    except ValueError as e:\n'
                 '        print("error:", e)',
            options=("ok 25 / error: invalid literal... / error: 100 too hot",
                     "ok 25 / error: invalid literal... / then a crash",
                     "ok 25 / ok 100"),
            answer=0,
            run=True,
            explain="Python's ValueError and YOUR ValueError are the same "
                    "type, so one `except ValueError` handles both.",
        ),
        Riddle(
            question="Why raise an exception instead of returning -1?",
            options=("It's faster",
                     "-1 could be real data; an exception can't be "
                     "mistaken for data and must be handled",
                     "Functions can't return negative numbers"),
            answer=1,
            explain="Exceptions are a separate channel for bad news.",
        ),
    ],
    trial=TRIAL_1,
    victory=[
        "Now when the sensor reads 100°C, the program doesn't blindly",
        "turn on the sprinklers: it raises an alarm, catches it, and",
        "tells the farmer exactly what's wrong.",
    ],
)


# ================================================================ chapter 2

CHAPTER_2 = Chapter(
    number=2,
    title="The Hydra of Many Heads",
    exercise="Exercise 2 - ft_different_errors.py (many error types)",
    rune="🐍 Rune of the Many Heads (multiple except)",
    story=[
        "In the flooded cellar of the greenhouse lives the Hydra.",
        "Each of its heads breathes a different curse:",
        "  one spits bad data, one divides by zero,",
        "  one hides files, one mixes things that can't be mixed.",
        "'One shield is not enough,' warns the Elder Gardener.",
        "'Learn the NAME of each curse, and you can block them all.'",
    ],
    pages=[
        Page([
            "Python has many exception types, so you can react",
            "differently to different problems:",
            "  ValueError         right type, bad value:  int('abc')",
            "  ZeroDivisionError  dividing by zero:       10 / 0",
            "  FileNotFoundError  missing file:           open('/nope')",
            "  TypeError          mixing types:           'Tomato' + 5",
            "  KeyError, IndexError, AttributeError ... and many more",
        ]),
        Page([
            "One try can have SEVERAL except clauses. Python checks them",
            "from top to bottom and runs only the FIRST that matches.",
            "Each clause knows which error it caught, so it can print the",
            "name - no need for type() (forbidden in the subject!).",
        ], 'try:\n'
           '    garden_operations(op)\n'
           'except ValueError as e:\n'
           '    print(f"Caught ValueError: {e}")\n'
           'except ZeroDivisionError as e:\n'
           '    print(f"Caught ZeroDivisionError: {e}")'),
        Page([
            "A tuple catches several types in ONE clause.",
            "`except Exception` catches (almost) everything, because",
            "exceptions form a family tree with Exception at the top:",
            "  Exception > ArithmeticError > ZeroDivisionError",
            "  Exception > OSError > FileNotFoundError",
            "So always put specific errors BEFORE general ones.",
        ], 'except (ValueError, TypeError) as e:\n'
           '    print("Bad data:", e)'),
        Page([
            "mypy will complain about 'Tomato' + 5. That's its job: it",
            "spots type errors before running! The subject says to keep",
            "this one on purpose, since we WANT the TypeError.",
        ]),
    ],
    monster=Monster(
        name="the Hydra",
        art=r"""
             _   ValueError    _
           _( )_ ZeroDivision _( )_
          (_ o _)  FileNotFound(_ o _)
            \ \    TypeError    / /
             \ \___/^^^^^\_____/ /
              \______~~~~______/
""",
        taunt="Four heads, four curses! Which one will you block?",
        defeat="Head after head, the Hydra is blocked by the right "
               "except. It sinks back into the cellar water.",
    ),
    riddles=[
        Riddle(
            question="Which exception does 10 / 0 raise?",
            code="10 / 0",
            options=("ValueError", "ZeroDivisionError", "TypeError",
                     "FileNotFoundError"),
            answer=1, run=True,
            explain="Dividing by zero is ZeroDivisionError.",
        ),
        Riddle(
            question="Which exception does this raise?",
            code='"Tomato" + 5',
            options=("ValueError", "TypeError", "ZeroDivisionError",
                     "No error, it gives 'Tomato5'"),
            answer=1, run=True,
            explain="str + int can't be mixed: TypeError.",
        ),
        Riddle(
            question="Which exception does this raise?",
            code='open("/non/existent/file")',
            options=("FileNotFoundError", "ValueError", "KeyError",
                     "Nothing, it creates the file"),
            answer=0, run=True,
            explain="Opening a missing file for reading: FileNotFoundError."
                    " Since it never opened, there's nothing to close().",
        ),
        Riddle(
            question="What does this print?",
            code='try:\n'
                 '    1 / 0\n'
                 'except ValueError:\n'
                 '    print("value")\n'
                 'except ZeroDivisionError:\n'
                 '    print("zero")\n'
                 'except Exception:\n'
                 '    print("something")',
            options=("value", "zero", "zero, something", "something"),
            answer=1, run=True,
            explain="Only the FIRST matching except runs. ValueError "
                    "doesn't match, ZeroDivisionError does, done.",
        ),
        Riddle(
            question="A trap! What does this print?",
            code='try:\n'
                 '    int("abc")\n'
                 'except Exception:\n'
                 '    print("general")\n'
                 'except ValueError:\n'
                 '    print("specific")',
            options=("specific", "general", "general, specific"),
            answer=1, run=True,
            explain="ValueError IS an Exception, so the general clause "
                    "matches first. Put specific errors first!",
        ),
        Riddle(
            question="What happens here?",
            code='for op in [0, 1, 2]:\n'
                 '    try:\n'
                 '        if op == 0:\n'
                 '            int("abc")\n'
                 '        elif op == 1:\n'
                 '            1 / 0\n'
                 '        else:\n'
                 '            [1, 2][5]\n'
                 '    except (ValueError, ZeroDivisionError) as e:\n'
                 '        print("caught:", e)',
            options=("Three 'caught' lines",
                     "Two 'caught' lines, then a crash (IndexError)",
                     "A crash right away"),
            answer=1, run=True,
            explain="The tuple catches only the types listed. [1, 2][5] is "
                    "an IndexError, which nobody catches!",
        ),
        Riddle(
            question="How do you print WHICH error was caught, without "
                     "type()?",
            options=("You can't",
                     "One except clause per error type, each prints its "
                     "own name",
                     "print(e) always shows the type's name"),
            answer=1,
            explain="print(e) shows only the message ('division by zero')."
                    " Each clause knows what it catches.",
        ),
    ],
    trial=TRIAL_2,
    victory=[
        "Different problems now get different answers: missing files",
        "are reported as missing, bad data as bad data. The farmers",
        "finally understand what their greenhouse is telling them.",
    ],
)


# ================================================================ chapter 3

CHAPTER_3 = Chapter(
    number=3,
    title="The Mimic Seeds",
    exercise="Exercise 3 - ft_custom_errors.py (your own error types)",
    rune="🧬 Rune of Creation (custom exceptions)",
    story=[
        "Strange seeds have sprouted in the greenhouse. They mimic real",
        "Python errors, but they're... different. A wilting tomato",
        "reports a ValueError. An empty water tank says KeyError.",
        "Nobody can tell a plant problem from a water problem!",
        "'Python's errors don't speak Garden,' sighs the Elder Gardener.",
        "'You must CREATE new ones. Name the problems of OUR world.'",
    ],
    pages=[
        Page([
            "An exception type is just a class that inherits from",
            "Exception. That's it - two lines!",
        ], 'class GardenError(Exception):\n'
           '    pass\n'
           '\n'
           'raise GardenError("Something is wrong in the garden")'),
        Page([
            "Inheritance builds a family tree. A PlantError IS ALSO a",
            "GardenError, so `except GardenError` catches both children.",
            "",
            "        Exception",
            "            │",
            "       GardenError",
            "        ┌───┴────┐",
            "   PlantError  WaterError",
        ], 'class PlantError(GardenError):\n'
           '    pass\n'
           '\n'
           'class WaterError(GardenError):\n'
           '    pass'),
        Page([
            "By default, str(GardenError()) is an empty string. To give",
            "a default message, write __init__ with a default argument,",
            "and pass the message to the parent with super().__init__().",
        ], 'class PlantError(GardenError):\n'
           '    def __init__(self, message: str = "Unknown plant error")'
           ' -> None:\n'
           '        super().__init__(message)'),
        Page([
            "When to create your own? When a built-in name would be",
            "vague or misleading. Your callers can then catch EXACTLY",
            "garden problems (except PlantError), or all of them at once",
            "(except GardenError), without catching unrelated bugs.",
        ]),
    ],
    monster=Monster(
        name="the Mimic Seedling",
        art=r"""
                 \ | /
               '- (?) -'     I am a ValueError... or am I?
                / | \
               (_/ \_)
              ~~~~~~~~~
""",
        taunt="Is it a plant problem? A water problem? Nobody knows!",
        defeat="Named at last, the Mimic Seedling can't hide. It "
               "shrivels into a perfectly labelled PlantError.",
    ),
    riddles=[
        Riddle(
            question="What does this print?",
            code='class GardenError(Exception):\n'
                 '    pass\n'
                 '\n'
                 'class PlantError(GardenError):\n'
                 '    pass\n'
                 '\n'
                 'try:\n'
                 '    raise PlantError("The tomato is wilting!")\n'
                 'except GardenError as e:\n'
                 '    print("Caught:", e)',
            options=("Caught: The tomato is wilting!",
                     "It crashes: PlantError isn't GardenError",
                     "Caught: PlantError"),
            answer=0, run=True,
            explain="A child is caught by its parent's except.",
        ),
        Riddle(
            question="The other way around?",
            code='class GardenError(Exception):\n'
                 '    pass\n'
                 '\n'
                 'class PlantError(GardenError):\n'
                 '    pass\n'
                 '\n'
                 'try:\n'
                 '    raise GardenError("Something is off")\n'
                 'except PlantError as e:\n'
                 '    print("Caught:", e)',
            options=("Caught: Something is off", "It crashes"),
            answer=1, run=True,
            explain="A GardenError is NOT necessarily a PlantError. "
                    "Parents catch children, never the reverse.",
        ),
        Riddle(
            question="What does this print?",
            code='class WaterError(Exception):\n'
                 '    pass\n'
                 '\n'
                 'print("[" + str(WaterError()) + "]")',
            options=("[WaterError]", "[]", "[Unknown water error]"),
            answer=1, run=True,
            explain="Without a message, the text is empty. That's why the "
                    "subject asks for a default message.",
        ),
        Riddle(
            question="What does this print?",
            code='class WaterError(Exception):\n'
                 '    def __init__(self, message: str = '
                 '"Unknown water error") -> None:\n'
                 '        super().__init__(message)\n'
                 '\n'
                 'print(WaterError())\n'
                 'print(WaterError("Not enough water in the tank!"))',
            options=("Unknown water error / Not enough water in the tank!",
                     "Unknown water error / Unknown water error",
                     "(empty) / Not enough water in the tank!"),
            answer=0, run=True,
            explain="The default is used only when no message is given.",
        ),
        Riddle(
            question="Fill the blank so PlantError is a garden problem:"
                     "   class PlantError(___________):",
            kind="blank",
            answer=("GardenError",),
            explain="The parent class goes between the parentheses.",
        ),
        Riddle(
            question="When should you create your own error types?",
            options=("Never, built-ins are enough",
                     "When a built-in would be vague: your own names let "
                     "callers catch exactly your problems, or all of them "
                     "via the parent",
                     "Only to make the code longer"),
            answer=1,
            explain="Clear names = clear code, and inheritance groups them.",
        ),
    ],
    trial=TRIAL_3,
    victory=[
        "Now a wilting tomato raises a PlantError and an empty tank a",
        "WaterError. And the night-watch program simply catches",
        "GardenError to hear about any garden trouble at all.",
    ],
)


# ================================================================ chapter 4

CHAPTER_4 = Chapter(
    number=4,
    title="The Eternal Fountain",
    exercise="Exercise 4 - ft_finally_block.py (finally)",
    rune="🛡 Rune of Always (finally)",
    story=[
        "At the heart of the greenhouse flows the Eternal Fountain that",
        "feeds the watering system. Whoever opens its valve MUST close",
        "it again - or the greenhouse floods.",
        "But last night an error struck while the valve was open... the",
        "program jumped to its except, and nobody closed the valve.",
        "The floor is now a lake. Frogs are holding a meeting.",
        "'There is one last spell,' the Elder Gardener says. 'A spell",
        "that runs ALWAYS. Error or not. Return or not.'",
    ],
    pages=[
        Page([
            "`finally:` runs after the try, no matter how it ends:",
            "  - the try worked           -> finally runs",
            "  - an error was caught      -> finally runs",
            "  - an error was NOT caught  -> finally runs, then the crash",
            "  - a return happened        -> finally runs before leaving",
        ], 'try:\n'
           '    print("Opening watering system")\n'
           '    water_plant("lettuce")      # may raise\n'
           'except PlantError as e:\n'
           '    print("Caught:", e)\n'
           'finally:\n'
           '    print("Closing watering system")'),
        Page([
            "That's why cleanup belongs in finally: closing files,",
            "network connections, valves... Put the closing line ONLY in",
            "finally - if you also put it in except, it runs twice.",
            "",
            "Bonus: `else:` runs only when the try had NO error.",
        ]),
        Page([
            "The subject wants test_watering_system() to STOP at the first",
            "invalid plant and return to main. A `return` inside except",
            "does exactly that - and finally still closes the system.",
            "",
            "'Tomato' is capitalized, 'lettuce' is not:",
            "   name == name.capitalize()",
        ], 'print("lettuce".capitalize())   # Lettuce'),
    ],
    monster=Monster(
        name="the Flood Serpent",
        art=r"""
          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ~~  ___      ~~~      ~~
          ~~   /o o\_____     ~~~
              (  ^         \__/\/\/\/~~
          ~~~  `-'~~~~~~~~~~~~~~~~~~~~
""",
        taunt="Raise an error while the valve is open and I'm FREE!",
        defeat="The valve clicks shut in its finally block. The Flood "
               "Serpent drains away. The frogs adjourn their meeting.",
    ),
    riddles=[
        Riddle(
            question="What does this print?",
            code='try:\n'
                 '    print("open")\n'
                 '    int("abc")\n'
                 '    print("work")\n'
                 'except ValueError:\n'
                 '    print("error")\n'
                 'finally:\n'
                 '    print("close")',
            options=("open / work / close", "open / error / close",
                     "open / error", "open / work / error / close"),
            answer=1, run=True,
            explain="Error -> except runs -> finally runs.",
        ),
        Riddle(
            question="And if nothing goes wrong?",
            code='try:\n'
                 '    print("open")\n'
                 '    print("work")\n'
                 'except ValueError:\n'
                 '    print("error")\n'
                 'finally:\n'
                 '    print("close")',
            options=("open / work", "open / work / close",
                     "open / work / error / close"),
            answer=1, run=True,
            explain="No error -> except is skipped, finally STILL runs.",
        ),
        Riddle(
            question="With a return inside except?",
            code='def water() -> None:\n'
                 '    try:\n'
                 '        print("open")\n'
                 '        raise ValueError("bad plant")\n'
                 '    except ValueError:\n'
                 '        print("caught")\n'
                 '        return\n'
                 '    finally:\n'
                 '        print("close")\n'
                 '    print("after")\n'
                 '\n'
                 'water()',
            options=("open / caught", "open / caught / close",
                     "open / caught / close / after"),
            answer=1, run=True,
            explain="return leaves the function, but finally runs on the "
                    "way out. 'after' is never reached.",
        ),
        Riddle(
            question="With an error NOBODY catches?",
            code='try:\n'
                 '    print("open")\n'
                 '    1 / 0\n'
                 'finally:\n'
                 '    print("close")',
            options=("open, then a crash", "open / close, then a crash",
                     "open / close, no crash"),
            answer=1, run=True,
            explain="finally runs even then - but it does NOT catch the "
                    "error. Only except catches.",
        ),
        Riddle(
            question="What does this print?",
            code='try:\n'
                 '    print("water Tomato")\n'
                 'except ValueError:\n'
                 '    print("error")\n'
                 'else:\n'
                 '    print("all plants OK")\n'
                 'finally:\n'
                 '    print("close")',
            options=("water Tomato / close",
                     "water Tomato / all plants OK / close",
                     "water Tomato / error / close"),
            answer=1, run=True,
            explain="else runs only when the try had no error.",
        ),
        Riddle(
            question="Fill the blank:   ________:  print('Closing system')"
                     "   (it must run no matter what)",
            kind="blank",
            answer=("finally",),
            explain="finally = always.",
        ),
    ],
    trial=TRIAL_4,
    victory=[
        "Errors still happen - plants get misspelled, sensors break -",
        "but the fountain valve closes every single time.",
        "The greenhouse is safe. Or... is it?",
    ],
)

CHAPTERS = [CHAPTER_0, CHAPTER_1, CHAPTER_2, CHAPTER_3, CHAPTER_4]


# ================================================================ finale

FINAL_STORY = [
    "The ground splits open. From the darkness rises MURPHY, the Blight",
    "King himself - lord of 'anything that can go wrong, will go wrong'.",
    "'Little Guardian,' he laughs, 'your forge spells were cute. But can",
    "you protect the REAL greenhouse? Can you explain your magic to the",
    "Council of Peers at your defense?'",
    "The Elder Gardener puts a hand on your shoulder. 'You're ready.'",
]

MURPHY = Monster(
    name="Murphy the Blight King",
    art=r"""
                   ___/\___/\___
                  /  ☠  WHAT  ☠ \     "Anything that can go wrong,
                 |   CAN GO      |      WILL go wrong!"
                 |    WRONG?     |
                  \___________/
                  /|  |   |  |\
""",
    taunt="Answer the Council's questions, if you understand your code!",
    defeat="Murphy roars and crumbles: no failure can crash a program "
           "guarded by someone who truly understands it.",
)

DEFENSE_RIDDLES = [
    Riddle(
        question="Council: 'Why does Python have DIFFERENT error types?'",
        options=("To look complicated",
                 "So each problem can be recognised and handled in its own "
                 "way - a missing file is not the same as bad data",
                 "Because old Python versions needed them"),
        answer=1,
        explain="Different types = different reactions.",
    ),
    Riddle(
        question="Council: 'In ex0, why doesn't input_temperature() "
                 "catch its own error?'",
        options=("It's a bug",
                 "Its job is only to convert; the caller decides what to "
                 "do with a failure, so the error travels up to the test",
                 "Because except is not authorized"),
        answer=1,
        explain="Raise where you detect the problem, catch where you can "
                "do something about it.",
    ),
    Riddle(
        question="Council: 'How do you catch several types with one try:?'",
        options=("Several except clauses, or one except with a tuple "
                 "like (ValueError, TypeError)",
                 "Use type(e) in an if",
                 "You need one try per type"),
        answer=0,
        explain="Both are valid; type() is forbidden anyway.",
    ),
    Riddle(
        question="Council: 'Why does catching GardenError also catch "
                 "PlantError?'",
        options=("Because PlantError inherits from GardenError: every "
                 "PlantError IS a GardenError",
                 "Because they're in the same file",
                 "Because except catches everything"),
        answer=0,
        explain="Inheritance is how exceptions are grouped.",
    ),
    Riddle(
        question="Council: 'Why clean up in finally, not after the try?'",
        options=("finally is faster",
                 "An error or a return could skip the code after the try;"
                 " finally runs no matter how the try ends",
                 "Python requires it"),
        answer=1,
        explain="That's the whole point of finally.",
    ),
    Riddle(
        question="Council: 'mypy complains about your TypeError line in "
                 "ex2. Is that a problem?'",
        options=("Yes, delete it",
                 "No: the subject says to keep it on purpose, since mypy's "
                 "job is to spot exactly that kind of type error",
                 "Disable mypy for the whole project"),
        answer=1,
        explain="Know WHY your tools complain - that's understanding.",
    ),
]
