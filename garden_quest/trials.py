"""The five forge trials, one per chapter.

Each trial mirrors one exercise of the Garden Guardian subject, with a
magical twist so you practise the *idea* rather than copy an answer.
When you reach the final chapter you write the real exercises yourself.
"""

import ast

from .forge import Check, ForgeFailure, ForgeTrial, Spell, call, calls_named
from .forge import need, uses


def _lines(text: str) -> list[str]:
    return [line for line in text.strip().splitlines() if line.strip()]


# ================================================================ trial 0

def _t0_valid(spell: Spell) -> None:
    result = call(need(spell, "read_mana"), "42")
    if result.error is not None:
        raise ForgeFailure(f"read_mana('42') raised {result.error!r}")
    if result.value != 42 or not isinstance(result.value, int):
        raise ForgeFailure(f"read_mana('42') returned {result.value!r}, "
                           "expected the integer 42")


def _t0_invalid(spell: Spell) -> None:
    result = call(need(spell, "read_mana"), "xyz")
    if not isinstance(result.error, ValueError):
        raise ForgeFailure(
            "read_mana('xyz') should let int() raise its ValueError, but "
            f"it gave {result.error or result.value!r}. "
            "(The catching happens in test_mana, not in read_mana!)")


def _t0_survives(spell: Spell) -> None:
    result = call(need(spell, "test_mana"))
    if result.error is not None:
        raise ForgeFailure(f"test_mana() crashed with {result.error!r}")
    out = result.output.lower()
    if "42" not in out:
        raise ForgeFailure("test_mana() should print the valid mana (42)")
    if "invalid literal" not in out:
        raise ForgeFailure("test_mana() should print the error message it "
                           "caught (hint: `except ValueError as e:` then "
                           "print e)")


def _t0_try(spell: Spell) -> None:
    if not uses(spell, ast.Try):
        raise ForgeFailure("I don't see any try/except in your file.")


TRIAL_0 = ForgeTrial(
    filename="trial0_mana_crystal.py",
    mission=[
        "The Mana Crystal whispers numbers... but sometimes it whispers",
        "gibberish. Write two functions:",
        "",
        "  read_mana(mana_str: str) -> int",
        "      turns the text into an int and returns it.",
        "      It does NOT catch errors itself.",
        "",
        "  test_mana() -> None",
        "      calls read_mana('42') and read_mana('xyz'), each inside its",
        "      own try/except, prints the result or the caught error, and",
        "      finishes without crashing.",
        "",
        "  (Exercise 0 in disguise: input_temperature/test_temperature)",
    ],
    skeleton='''
"""Forge trial 0 - The Mana Crystal."""


def read_mana(mana_str: str) -> int:
    # TODO: convert mana_str to an int and return it
    pass


def test_mana() -> None:
    print("=== Mana Crystal ===")
    # TODO: try read_mana("42") and print the result
    # TODO: try read_mana("xyz") and catch the error, print it
    # TODO: print a final message to prove the program didn't crash


if __name__ == "__main__":
    test_mana()
''',
    hints=[
        "int('42') gives 42, int('xyz') raises ValueError. read_mana only "
        "needs one line.",
        "In test_mana, put the call in `try:` and add `except ValueError as "
        "e:` - `e` is the error object, print(e) shows its message.",
        "Shape: try: / value = read_mana('xyz') / print(...) / except "
        "ValueError as e: / print(f'Caught read_mana error: {e}')",
    ],
    checks=[
        ("read_mana('42') returns 42", _t0_valid),
        ("read_mana('xyz') lets ValueError escape", _t0_invalid),
        ("test_mana() survives and reports both cases", _t0_survives),
        ("you used try/except", _t0_try),
    ],
)


# ================================================================ trial 1

def _t1_limits(spell: Spell) -> None:
    read = need(spell, "read_mana")
    for text, number in (("42", 42), ("0", 0), ("100", 100)):
        result = call(read, text)
        if result.error is not None or result.value != number:
            raise ForgeFailure(
                f"read_mana({text!r}) should return {number} (limits are "
                f"included!) - got {result.value!r} / {result.error!r}")


def _t1_raise(text: str) -> Check:
    def check(spell: Spell) -> None:
        result = call(need(spell, "read_mana"), text)
        if not isinstance(result.error, ValueError):
            raise ForgeFailure(
                f"read_mana({text!r}) should raise a ValueError, got "
                f"{result.error!r} / returned {result.value!r}")
        if text.lstrip("-").isdigit() and text not in str(result.error):
            raise ForgeFailure(
                f"the error message should mention the value {text}: "
                f"{str(result.error)!r}")
    return check


def _t1_survives(spell: Spell) -> None:
    result = call(need(spell, "test_mana"))
    if result.error is not None:
        raise ForgeFailure(f"test_mana() crashed with {result.error!r}")
    for value in ("42", "xyz", "150", "-7"):
        if value not in result.output:
            raise ForgeFailure(f"test_mana() should also test {value!r}")


def _t1_uses_raise(spell: Spell) -> None:
    if not uses(spell, ast.Raise):
        raise ForgeFailure("you need the `raise` keyword somewhere!")


TRIAL_1 = ForgeTrial(
    filename="trial1_dragon_mana.py",
    mission=[
        "Too little mana and spells fizzle. Too much and the Ember Drake",
        "awakens. Upgrade your crystal reader:",
        "",
        "  read_mana(mana_str: str) -> int",
        "      converts like before, then checks 0 <= mana <= 100.",
        "      Outside that range: raise ValueError with a message that",
        "      includes the number, e.g. '150 is too much mana (max 100)'.",
        "",
        "  test_mana() -> None",
        "      tests '42', 'xyz', '150' and '-7' without crashing.",
        "",
        "  (Exercise 1 in disguise: plants need 0 to 40 degrees)",
    ],
    skeleton='''
"""Forge trial 1 - The Ember Drake's mana limits."""


def read_mana(mana_str: str) -> int:
    mana = int(mana_str)
    # TODO: if mana is too high, raise ValueError(...)
    # TODO: if mana is too low,  raise ValueError(...)
    return mana


def test_mana() -> None:
    print("=== Mana Limits ===")
    # TODO: test "42", "xyz", "150" and "-7"
    # (a loop over a list of test values keeps it short!)


if __name__ == "__main__":
    test_mana()
''',
    hints=[
        "`raise ValueError('message')` stops the function immediately and "
        "sends the error up to whoever called it.",
        "An f-string builds the message: raise ValueError(f'{mana} is too "
        "much mana (max 100)')",
        "Limits included means 0 and 100 are fine: test `mana > 100` and "
        "`mana < 0`. In test_mana: for text in ['42', 'xyz', '150', '-7']: "
        "try: ... except ValueError as e: ...",
    ],
    checks=[
        ("valid values (42, 0 and 100) are returned", _t1_limits),
        ("'150' raises a ValueError mentioning 150", _t1_raise("150")),
        ("'-7' raises a ValueError mentioning -7", _t1_raise("-7")),
        ("'xyz' still raises ValueError", _t1_raise("xyz")),
        ("test_mana() tests all four values without crashing",
         _t1_survives),
        ("you used `raise`", _t1_uses_raise),
    ],
)


# ================================================================ trial 2

HYDRA_HEADS = (ValueError, ZeroDivisionError, FileNotFoundError, TypeError)


def _t2_head(number: int) -> Check:
    expected = HYDRA_HEADS[number]

    def check(spell: Spell) -> None:
        result = call(need(spell, "cast_spell"), number)
        if result.error is None or not isinstance(result.error, expected):
            raise ForgeFailure(
                f"cast_spell({number}) should raise {expected.__name__}, "
                f"got {result.error!r}")
    return check


def _t2_calm(spell: Spell) -> None:
    for number in (4, 99, -1):
        result = call(need(spell, "cast_spell"), number)
        if result.error is not None:
            raise ForgeFailure(f"cast_spell({number}) should just return, "
                               f"but raised {result.error!r}")


def _t2_survives(spell: Spell) -> None:
    result = call(need(spell, "test_spells"))
    if result.error is not None:
        raise ForgeFailure(f"test_spells() crashed with {result.error!r}")
    for head in HYDRA_HEADS:
        if head.__name__ not in result.output:
            raise ForgeFailure(f"test_spells() should report the "
                               f"{head.__name__} it caught")


def _t2_many_heads(spell: Spell) -> None:
    for node in ast.walk(spell.tree):
        if isinstance(node, ast.Try) and len(node.handlers) >= 2:
            return
        if isinstance(node, ast.ExceptHandler):
            if isinstance(node.type, ast.Tuple):
                return
    raise ForgeFailure("show one try: with several except clauses, or one "
                       "`except (ErrorA, ErrorB):`")


def _t2_no_type(spell: Spell) -> None:
    if calls_named(spell, "type"):
        raise ForgeFailure("the subject forbids type(). Let each except "
                           "clause know which error it caught!")


TRIAL_2 = ForgeTrial(
    filename="trial2_hydra.py",
    mission=[
        "The Hydra has four heads, each one a different error.",
        "",
        "  cast_spell(spell_number: int) -> None",
        "      0 -> faulty code that raises ValueError",
        "      1 -> faulty code that raises ZeroDivisionError",
        "      2 -> faulty code that raises FileNotFoundError",
        "      3 -> faulty code that raises TypeError",
        "      anything else -> just return",
        "      Write *real* faulty code (int('abc'), 1 / 0, ...), not raise.",
        "",
        "  test_spells() -> None",
        "      tries spells 0..4, catches each error *by its type* and prints",
        "      its name and message. Without using type()!",
        "",
        "  (Exercise 2 in disguise: garden_operations/test_error_types)",
    ],
    skeleton='''
"""Forge trial 2 - The Hydra of Many Heads."""


def cast_spell(spell_number: int) -> None:
    if spell_number == 0:
        pass  # TODO: faulty code -> ValueError
    elif spell_number == 1:
        pass  # TODO: faulty code -> ZeroDivisionError
    # TODO: 2 -> FileNotFoundError, 3 -> TypeError


def test_spells() -> None:
    print("=== Hydra Battle ===")
    # TODO: for each spell number 0..4:
    #           try the spell
    #           except each error type separately, print its name + message


if __name__ == "__main__":
    test_spells()
''',
    hints=[
        "Faulty code ideas: int('abc'), 10 / 0, open('/no/such/file'), "
        "'mana' + 5.",
        "One try can have many except clauses: Python checks them from top "
        "to bottom and runs the FIRST one that matches.",
        "except ValueError as e: print(f'Caught ValueError: {e}') - repeat "
        "for each type. mypy will complain about 'mana' + 5: that's expected"
        " (add `# type: ignore` if you want it quiet).",
    ],
    checks=[
        ("cast_spell(0) raises ValueError", _t2_head(0)),
        ("cast_spell(1) raises ZeroDivisionError", _t2_head(1)),
        ("cast_spell(2) raises FileNotFoundError", _t2_head(2)),
        ("cast_spell(3) raises TypeError", _t2_head(3)),
        ("other numbers return calmly", _t2_calm),
        ("test_spells() names each error and survives", _t2_survives),
        ("several error types caught by one try", _t2_many_heads),
        ("no type() used", _t2_no_type),
    ],
)


# ================================================================ trial 3

def _t3_family(spell: Spell) -> None:
    magic = need(spell, "MagicError")
    potion = need(spell, "PotionError")
    curse = need(spell, "CurseError")
    for cls in (magic, potion, curse):
        if not isinstance(cls, type):
            raise ForgeFailure(f"{cls!r} should be a class")
    if not issubclass(magic, Exception):
        raise ForgeFailure("MagicError must inherit from Exception")
    for cls in (potion, curse):
        if not issubclass(cls, magic):
            raise ForgeFailure(f"{cls.__name__} must inherit from "
                               "MagicError")
    if issubclass(potion, curse) or issubclass(curse, potion):
        raise ForgeFailure("PotionError and CurseError are siblings, not "
                           "parent and child")


def _t3_defaults(spell: Spell) -> None:
    for name in ("MagicError", "PotionError", "CurseError"):
        result = call(need(spell, name))
        if result.error is not None:
            raise ForgeFailure(f"{name}() crashed: {result.error!r}")
        if str(result.value) == "":
            raise ForgeFailure(
                f"str({name}()) is empty - give it a default message "
                "(see the mission text)")


def _t3_custom(spell: Spell) -> None:
    text = "The potion boiled over!"
    for name in ("PotionError", "CurseError"):
        result = call(need(spell, name), text)
        if result.error is not None or str(result.value) != text:
            raise ForgeFailure(f"{name}({text!r}) should keep that message,"
                               f" got {str(result.value)!r}")


def _t3_raisers(spell: Spell) -> None:
    for function, cls in (("brew_potion", "PotionError"),
                          ("break_curse", "CurseError")):
        result = call(need(spell, function))
        if not isinstance(result.error, need(spell, cls)):
            raise ForgeFailure(f"{function}() should raise {cls}, got "
                               f"{result.error!r}")


def _t3_survives(spell: Spell) -> None:
    result = call(need(spell, "test_magic_errors"))
    if result.error is not None:
        raise ForgeFailure(f"test_magic_errors() crashed: {result.error!r}")
    for word in ("PotionError", "CurseError", "MagicError"):
        if word not in result.output:
            raise ForgeFailure(f"the output should show a caught {word}")


TRIAL_3 = ForgeTrial(
    filename="trial3_mimic_errors.py",
    mission=[
        "Python's errors don't know about potions and curses. Make your own!",
        "",
        "  class MagicError(Exception)      default 'Unknown magic error'",
        "  class PotionError(MagicError)    default 'Unknown potion error'",
        "  class CurseError(MagicError)     default 'Unknown curse error'",
        "",
        "  brew_potion() -> None  raises PotionError('The potion boiled!')",
        "  break_curse() -> None   raises CurseError('The curse bites back!')",
        "",
        "  test_magic_errors() -> None",
        "      catches PotionError, then CurseError specifically, then shows",
        "      that `except MagicError` catches BOTH.",
        "",
        "  (Exercise 3 in disguise: GardenError, PlantError, WaterError)",
    ],
    skeleton='''
"""Forge trial 3 - The Mimic Seeds: your own error types."""


class MagicError(Exception):
    # TODO: give it a default message
    pass


# TODO: class PotionError(...)
# TODO: class CurseError(...)


def brew_potion() -> None:
    # TODO: raise a PotionError with a message
    pass


def break_curse() -> None:
    # TODO: raise a CurseError with a message
    pass


def test_magic_errors() -> None:
    print("=== Custom Magic Errors ===")
    # TODO: catch PotionError from brew_potion()
    # TODO: catch CurseError from break_curse()
    # TODO: catch both with `except MagicError`


if __name__ == "__main__":
    test_magic_errors()
''',
    hints=[
        "A class in parentheses is its parent: `class PotionError(MagicError)`"
        " means every PotionError IS ALSO a MagicError.",
        "Default message: def __init__(self, message: str = 'Unknown potion "
        "error') -> None:  then  super().__init__(message)",
        "except MagicError catches any child class. Loop over "
        "[brew_potion, break_curse] and call each inside one try.",
    ],
    checks=[
        ("the error family tree is correct", _t3_family),
        ("each error has a default message", _t3_defaults),
        ("a custom message is kept", _t3_custom),
        ("brew_potion/break_curse raise the right error", _t3_raisers),
        ("test_magic_errors() catches them all and survives", _t3_survives),
    ],
)


# ================================================================ trial 4

def _t4_plant(spell: Spell) -> None:
    need(spell, "CurseError")
    result = call(need(spell, "enchant_plant"), "Rose")
    if result.error is not None:
        raise ForgeFailure(f"enchant_plant('Rose') raised {result.error!r}")
    if "Rose" not in result.output:
        raise ForgeFailure("enchant_plant('Rose') should print a success "
                           "message with the plant's name")


def _t4_bad_plant(spell: Spell) -> None:
    result = call(need(spell, "enchant_plant"), "rose")
    if not isinstance(result.error, need(spell, "CurseError")):
        raise ForgeFailure(f"enchant_plant('rose') should raise CurseError, "
                           f"got {result.error!r}")
    if "rose" not in str(result.error):
        raise ForgeFailure("the error message should contain the bad name")


def _t4_garden(plants: list[str], stop: str) -> Check:
    def check(spell: Spell) -> None:
        result = call(need(spell, "enchant_garden"), plants)
        if result.error is not None:
            raise ForgeFailure(f"enchant_garden({plants}) let an error "
                               f"escape: {result.error!r}")
        lines = _lines(result.output)
        if not lines or "open" not in lines[0].lower():
            raise ForgeFailure("the first line should open the moonwell")
        if "clos" not in lines[-1].lower():
            raise ForgeFailure("the LAST line should close the moonwell")
        closes = [line for line in lines if "clos" in line.lower()]
        if len(closes) != 1:
            raise ForgeFailure(f"the moonwell closed {len(closes)} times! "
                               "Close it once, only in `finally`.")
        if stop and stop in result.output:
            raise ForgeFailure(f"after the error, {stop!r} should not be "
                               "enchanted: stop and return immediately")
    return check


def _t4_finally(spell: Spell) -> None:
    for node in ast.walk(spell.tree):
        if isinstance(node, ast.Try) and node.finalbody:
            return
    raise ForgeFailure("I don't see a `finally:` block")


def _t4_survives(spell: Spell) -> None:
    result = call(need(spell, "test_moonwell"))
    if result.error is not None:
        raise ForgeFailure(f"test_moonwell() crashed: {result.error!r}")


TRIAL_4 = ForgeTrial(
    filename="trial4_moonwell.py",
    mission=[
        "The Moonwell must ALWAYS be closed, or its magic leaks away.",
        "",
        "  class CurseError(Exception)   (copy yours from trial 3)",
        "",
        "  enchant_plant(plant_name: str) -> None",
        "      if the name is capitalized ('Rose'): print a success message",
        "      otherwise ('rose'): raise CurseError with the bad name",
        "",
        "  enchant_garden(plants: list[str]) -> None",
        "      print 'Opening the moonwell', enchant each plant.",
        "      On CurseError: print it, then return immediately.",
        "      In `finally`: print 'Closing the moonwell'.",
        "",
        "  test_moonwell() -> None",
        "      calls enchant_garden with good plants, then with a bad one.",
        "",
        "  (Exercise 4 in disguise: water_plant/test_watering_system)",
    ],
    skeleton='''
"""Forge trial 4 - The Eternal Moonwell: finally always runs."""


class CurseError(Exception):
    pass  # TODO: paste your CurseError from trial 3


def enchant_plant(plant_name: str) -> None:
    # TODO: success if plant_name == plant_name.capitalize()
    # TODO: otherwise raise CurseError(...)
    pass


def enchant_garden(plants: list[str]) -> None:
    print("Opening the moonwell")
    # TODO: try / except CurseError / finally


def test_moonwell() -> None:
    print("=== The Eternal Moonwell ===")
    enchant_garden(["Rose", "Lily", "Sage"])
    print()
    enchant_garden(["Rose", "daisy", "Lily"])


if __name__ == "__main__":
    test_moonwell()
''',
    hints=[
        "'rose'.capitalize() is 'Rose'. A name is fine when it equals its "
        "capitalized version.",
        "Put the whole `for plant in plants:` loop inside the try, so the "
        "first CurseError jumps out of the loop to the except.",
        "`return` inside except still runs `finally` before leaving the "
        "function. That's the magic: print the closing line ONLY in finally.",
    ],
    checks=[
        ("enchant_plant('Rose') succeeds", _t4_plant),
        ("enchant_plant('rose') raises CurseError", _t4_bad_plant),
        ("good garden: open, enchant, close once",
         _t4_garden(["Rose", "Lily"], "")),
        ("bad garden: stops at 'daisy' but still closes once",
         _t4_garden(["Rose", "daisy", "Lily"], "Lily")),
        ("you used `finally`", _t4_finally),
        ("test_moonwell() survives", _t4_survives),
    ],
)
