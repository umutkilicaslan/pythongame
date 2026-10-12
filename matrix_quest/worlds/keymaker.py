"""World 4 - The Keymaker: Data Archivist (files and streams).

Trials: the Keymaker's doors instead of the archives' fragments, and a
~ marker instead of the 2087 # marker.
"""

import ast
from pathlib import Path

from ..forge import (ForgeFailure, ScriptResult, Spell, call, calls_named,
                     need, no_crash, script, uses)
from ..model import (Chapter, Enemy, Exercise, Line, Page, Riddle, Run,
                     Trial, World)
from . import art

KEYMAKER = "The Keymaker"

KEYS = ("[KEY 001] The door to the Source\n"
        "[KEY 002] The door to the Mainframe\n"
        "[KEY 003] The door back home\n")

FRAGMENT = ("[FRAGMENT 001] Digital preservation protocols established 2087"
            "\n[FRAGMENT 002] Knowledge must survive the entropy wars\n"
            "[FRAGMENT 003] Every byte saved is a victory against oblivion"
            "\n")


def _keys(spell: Spell) -> Path:
    path = spell.tmp / "keys.txt"
    path.write_text(KEYS)
    return path


def _run(spell: Spell, args: list[str], stdin: str = "") -> ScriptResult:
    result = script(spell, args, stdin)
    no_crash(result, "`python3 " + " ".join([spell.path.name] + args) + "`")
    return result


def _no_with(spell: Spell) -> None:
    if uses(spell, ast.With):
        raise ForgeFailure("the with statement is only allowed in the last "
                           "chapter: use open() and .close() here")


# ============================================================ chapter 0

def _c0_usage(spell: Spell) -> None:
    out = _run(spell, []).stdout
    if "Usage" not in out:
        raise ForgeFailure("without a file name, print 'Usage: ...'")


def _c0_missing(spell: Spell) -> None:
    out = _run(spell, ["no_such_door.txt"]).stdout
    if "Errno 2" not in out:
        raise ForgeFailure("a missing file should print the error, e.g. "
                           "[Errno 2] No such file or directory")


def _c0_directory(spell: Spell) -> None:
    out = _run(spell, [str(spell.tmp)]).stdout
    if "Errno" not in out:
        raise ForgeFailure("opening a folder fails too: catch OSError and "
                           "print the error")


def _c0_read(spell: Spell) -> None:
    _keys(spell)
    out = _run(spell, ["keys.txt"]).stdout
    if "[KEY 002] The door to the Mainframe" not in out:
        raise ForgeFailure("the file's content should be displayed")
    if "closed" not in out.split("[KEY 003]")[-1]:
        raise ForgeFailure("after the content, print that the door (file) "
                           "is closed")


def _c0_close(spell: Spell) -> None:
    _no_with(spell)
    for node in ast.walk(spell.tree):
        if isinstance(node, ast.Call) and isinstance(node.func,
                                                     ast.Attribute):
            if node.func.attr == "close":
                return
    raise ForgeFailure("close the file with .close()")


TRIAL_0 = Trial(
    id="w4c0",
    filename="w4_0_door.py",
    mission=[
        "Each door hides a file. Read the one given on the command line",
        "and show it like `cat` would:",
        "",
        "  $ python3 w4_0_door.py keys.txt",
        "  === The Keymaker's Doors ===",
        "  Opening door 'keys.txt'",
        "  ---",
        "  <the file's content>",
        "  ---",
        "  Door 'keys.txt' closed.",
        "",
        "  no argument     -> Usage: w4_0_door.py <file>",
        "  can't open it   -> Error opening door 'x': [Errno 2] No such...",
        "",
        "No `with` yet: open() and .close(). The workshop has a keys.txt",
        "to try with the Run button.",
        "",
        "Subject: ex0/ft_ancient_text.py.",
    ],
    skeleton='''import sys


if __name__ == "__main__":
    # TODO: usage message if there's no argument
    print("=== The Keymaker's Doors ===")
    # TODO: open, read, display, close - and catch the errors
''',
    hints=[
        "file = open(name) returns a file object (typing.IO); file.read() "
        "gives its whole text; file.close() releases it.",
        "Missing file -> FileNotFoundError, no rights -> PermissionError, a"
        " folder -> IsADirectoryError. They all inherit from OSError!",
        "print(f\"Error opening door '{name}': {e}\") inside "
        "except OSError as e:",
    ],
    checks=[
        ("no argument prints the usage", _c0_usage),
        ("a missing file is reported", _c0_missing),
        ("a folder is reported, no crash", _c0_directory),
        ("a real file is displayed, then closed", _c0_read),
        ("open/close without `with`", _c0_close),
    ],
    run_args="keys.txt",
)


# ============================================================ chapter 1

def _c1_transform(spell: Spell) -> None:
    _keys(spell)
    out = _run(spell, ["keys.txt"], "\n").stdout
    if "[KEY 001] The door to the Source~" not in out:
        raise ForgeFailure("show the transformed content: each line ends "
                           "with ~")
    if "Not saving" not in out:
        raise ForgeFailure("an empty name means 'Not saving data.'")


def _c1_save(spell: Spell) -> None:
    _keys(spell)
    out = _run(spell, ["keys.txt"], "copy.txt\n").stdout
    saved = spell.tmp / "copy.txt"
    if not saved.exists():
        raise ForgeFailure("typing copy.txt should create copy.txt")
    lines = saved.read_text().splitlines()
    if len(lines) != 3 or not all(line.endswith("~") for line in lines):
        raise ForgeFailure(f"copy.txt should hold the 3 transformed lines,"
                           f" got {saved.read_text()!r}")
    if "saved" not in out.lower():
        raise ForgeFailure("print a message saying the data was saved")


def _c1_replace(spell: Spell) -> None:
    _keys(spell)
    (spell.tmp / "copy.txt").write_text("old content that must go\n")
    _run(spell, ["keys.txt"], "copy.txt\n")
    if "old content" in (spell.tmp / "copy.txt").read_text():
        raise ForgeFailure("an existing file must be REPLACED: open it with"
                           " 'w'")


TRIAL_1 = Trial(
    id="w4c1",
    filename="w4_1_copy.py",
    mission=[
        "The Keymaker cuts copies. Start from your door reader, then:",
        "",
        "  - add a ~ at the end of every line (Zion-compatible)",
        "  - print 'Transform data:' and the new content between ---",
        "  - ask  Enter new file name (or empty):  with input()",
        "  - empty -> 'Not saving data.'",
        "  - otherwise: 'Saving data to 'x'', write the file (create it,",
        "    or replace it), then 'Data saved in file 'x'.'",
        "",
        "Still no `with`. Try the Run button with input: copy.txt",
        "",
        "Subject: ex1/ft_archive_creation.py.",
    ],
    skeleton='''import sys


if __name__ == "__main__":
    # TODO: your door reader from the previous chapter
    # TODO: transform, display, ask, save
    pass
''',
    hints=[
        "content.split('\\n') or .splitlines() gives the lines; "
        "'\\n'.join(...) glues them back.",
        "open(name, 'w') creates the file, or empties it if it exists. "
        "Then .write(text) and .close().",
        "Writing can fail too (a folder, no rights): catch OSError around "
        "the save.",
    ],
    checks=[
        ("lines get a ~ and an empty name skips saving", _c1_transform),
        ("a name saves the transformed copy", _c1_save),
        ("an existing file is replaced", _c1_replace),
        ("still open/close without `with`", _no_with),
    ],
    run_args="keys.txt",
    run_stdin="copy.txt\n",
)


# ============================================================ chapter 2

def _c2_stderr(spell: Spell) -> None:
    result = _run(spell, ["no_such_door.txt"])
    if "[STDERR]" not in result.stderr or "Errno 2" not in result.stderr:
        raise ForgeFailure("errors go to sys.stderr with a [STDERR] prefix "
                           f"(stderr was {result.stderr.strip()!r})")
    if "Errno" in result.stdout:
        raise ForgeFailure("the error should NOT appear on stdout")


def _c2_save_error(spell: Spell) -> None:
    _keys(spell)
    result = _run(spell, ["keys.txt"], str(spell.tmp) + "\n")
    if "[STDERR]" not in result.stderr:
        raise ForgeFailure("saving to a folder fails: report it on stderr")
    if "not saved" not in result.stdout.lower():
        raise ForgeFailure("then print 'Data not saved.' on stdout")


def _c2_stdin(spell: Spell) -> None:
    _keys(spell)
    _run(spell, ["keys.txt"], "copy.txt\n")
    if not (spell.tmp / "copy.txt").exists():
        raise ForgeFailure("the name read from stdin should be used to save")
    if calls_named(spell, "input"):
        raise ForgeFailure("input() is not allowed: use sys.stdin.readline()")
    if "sys.stdin" not in spell.source:
        raise ForgeFailure("read the answer from sys.stdin")


TRIAL_2 = Trial(
    id="w4c2",
    filename="w4_2_channels.py",
    mission=[
        "Three channels, older than the Internet: stdin, stdout, stderr.",
        "Upgrade your copier:",
        "",
        "  - every error message goes to sys.stderr, prefixed [STDERR]",
        "      [STDERR] Error opening door 'x': [Errno 2] ...",
        "  - a failed save prints the error on stderr, then",
        "      'Data not saved.' on stdout",
        "  - read the file name WITHOUT input(): write the prompt with",
        "    sys.stdout.write() + flush(), read with sys.stdin.readline()",
        "",
        "Subject: ex2/ft_stream_management.py.",
    ],
    skeleton='''import sys


if __name__ == "__main__":
    # TODO: your copier, with errors on stderr and no input()
    pass
''',
    hints=[
        "print(..., file=sys.stderr) or sys.stderr.write('...\\n').",
        "sys.stdout.write(prompt) doesn't add a new line; "
        "sys.stdout.flush() makes it appear right away.",
        "sys.stdin.readline() keeps the '\\n' at the end: .strip() it.",
    ],
    checks=[
        ("errors go to stderr with [STDERR]", _c2_stderr),
        ("a failed save is reported", _c2_save_error),
        ("the name comes from sys.stdin, not input()", _c2_stdin),
        ("still no `with`", _no_with),
    ],
    run_args="no_such_door.txt",
)


# ============================================================ chapter 3

def _vault(spell: Spell, *args: str) -> tuple[bool, str]:
    result = call(need(spell, "secure_vault"), *args)
    if result.error is not None:
        raise ForgeFailure(f"secure_vault{args} let an error escape: "
                           f"{result.error!r}")
    value = result.value
    if not (isinstance(value, tuple) and len(value) == 2 and
            isinstance(value[0], bool) and isinstance(value[1], str)):
        raise ForgeFailure(f"secure_vault should return (bool, str), got "
                           f"{value!r}")
    return value


def _c3_missing(spell: Spell) -> None:
    ok, text = _vault(spell, str(spell.tmp / "nope.txt"))
    if ok or "No such file" not in text:
        raise ForgeFailure(f"reading a missing file: (False, error "
                           f"message), got {(ok, text)!r}")
    ok, _ = _vault(spell, str(spell.tmp))
    if ok:
        raise ForgeFailure("reading a folder should fail: (False, ...)")


def _c3_read(spell: Spell) -> None:
    path = _keys(spell)
    if _vault(spell, str(path)) != (True, KEYS):
        raise ForgeFailure("reading keys.txt should give (True, <its whole "
                           "content>)")


def _c3_write(spell: Spell) -> None:
    path = spell.tmp / "vault.txt"
    ok, _ = _vault(spell, str(path), "write", "Neo was here\n")
    if not ok or not path.exists() or path.read_text() != "Neo was "\
            "here\n":
        raise ForgeFailure("secure_vault(name, 'write', text) should write "
                           "the text and return (True, ...)")
    ok, _ = _vault(spell, str(spell.tmp), "write", "x")
    if ok:
        raise ForgeFailure("writing to a folder should give (False, ...)")


def _c3_with(spell: Spell) -> None:
    if not uses(spell, ast.With):
        raise ForgeFailure("this chapter is all about the with statement")


TRIAL_3 = Trial(
    id="w4c3",
    filename="w4_3_vault.py",
    mission=[
        "The final vault closes by itself - even when things go wrong.",
        "",
        "  secure_vault(filename: str, action: str = 'read',",
        "               content: str = '') -> tuple[bool, str]",
        "      'read'  -> (True, the file's content)",
        "      'write' -> writes content, (True, 'Content successfully",
        "                 written to file')",
        "      any failure -> (False, the error message)",
        "      The file is opened with `with` - nothing escapes the vault.",
        "",
        "Main guard: try a missing file, a folder, keys.txt, and a write.",
        "",
        "Subject: ex3/ft_vault_security.py (secure_archive).",
    ],
    skeleton='''def secure_vault(filename: str, action: str = "read",
                 content: str = "") -> tuple[bool, str]:
    # TODO: with open(...) as file: ...
    return (False, "not implemented")


if __name__ == "__main__":
    print("=== The Keymaker's Vault ===")
    print(secure_vault("/not/existing/file"))
''',
    hints=[
        "with open(filename) as file: content = file.read()  - the file "
        "closes when the block ends, even if an exception flies out.",
        "Wrap the with in try/except OSError as e: and return (False, "
        "str(e)).",
        "One function, two modes: if action == 'write': open with 'w' "
        "and file.write(content).",
    ],
    checks=[
        ("failures return (False, message)", _c3_missing),
        ("reading returns (True, content)", _c3_read),
        ("writing works, and fails safely", _c3_write),
        ("the with statement is used", _c3_with),
    ],
)


# ============================================================ the story

CHAPTERS = [
    Chapter(
        id="w4c0",
        title="The Keymaker's Doors",
        exercise="ex0 · ft_ancient_text.py",
        concept="open() · read() · close() · OSError",
        story=[
            Line(KEYMAKER, "I have been waiting for you. I have many keys,"
                 " and many doors."),
            Line(KEYMAKER, "Each door hides a file. To read what is "
                 "inside, you must open it - and never forget to close "
                 "it."),
        ],
        pages=[
            Page("Opening a file", [
                "open(name) returns a file object (its type: typing.IO). "
                ".read() gives the whole text, .close() releases the file "
                "so the system can reuse it.",
            ], 'file = open("keys.txt")\n'
               'print(file.read())\n'
               'file.close()'),
            Page("When doors are locked", [
                "Opening can fail: FileNotFoundError (missing), "
                "PermissionError (no rights), IsADirectoryError (a "
                "folder). All of them inherit from OSError, so one except "
                "catches them all.",
            ], 'try:\n'
               '    file = open("no_such_door.txt")\n'
               'except OSError as e:\n'
               '    print(f"Error opening door: {e}")'),
        ],
        enemy=Enemy("the Locked Door", art.DOOR,
                    "*click* (it doesn't open)",
                    "The Keymaker smiles: \"Every door can be opened... "
                    "with the right key.\""),
        riddles=[
            Riddle("What does this print?", run=True,
                   code='try:\n    open("/no/such/file")\n'
                        'except OSError as e:\n    print(e)',
                   options=("[Errno 2] No such file or directory: "
                            "'/no/such/file'", "None", "It crashes"),
                   answer=0, explain="FileNotFoundError is an OSError."),
            Riddle("Is FileNotFoundError a kind of OSError?", run=True,
                   code='print(issubclass(FileNotFoundError, OSError))',
                   options=("True", "False"), answer=0,
                   explain="So except OSError catches missing files, "
                           "permissions and folders."),
            Riddle("Why call .close()?",
                   options=("It deletes the file",
                            "It releases the file: the system can only "
                            "keep a limited number open, and writes are "
                            "only guaranteed after closing"),
                   answer=1, explain="Always close what you open."),
            Riddle("What type of object does open() return?",
                   code='import tempfile\n\n'
                        'with tempfile.TemporaryFile("w+") as f:\n'
                        '    print(type(f).__name__)',
                   options=("str", "TextIOWrapper (a file object, "
                            "typing.IO)", "list"),
                   answer=1, run=True,
                   explain="Not the text itself: a handle on the file. "
                           ".read() gives the text."),
        ],
        trial=TRIAL_0,
        victory=[Line(KEYMAKER, "You read the door. And you closed it. "
                      "Good.")],
    ),
    Chapter(
        id="w4c1",
        title="Copying the Keys",
        exercise="ex1 · ft_archive_creation.py",
        concept="writing files · 'w' mode · input()",
        story=[
            Line(KEYMAKER, "A key is useless if it's lost. I always make a"
                 " copy."),
            Line(KEYMAKER, "Mark every line - the people of Zion will "
                 "recognise it. Then write it to a new file."),
        ],
        pages=[
            Page("Writing", [
                "open(name, 'w') creates the file, or EMPTIES it if it "
                "already exists. .write(text) writes a string (no automatic"
                " new line!).",
            ], 'file = open("copy.txt", "w")\n'
               'file.write("first line\\n")\n'
               'file.write("second line\\n")\n'
               'file.close()\n'
               'print(open("copy.txt").read())'),
            Page("Transforming lines", [
                "splitlines() cuts a text into lines; a loop or a "
                "comprehension changes each one; '\\n'.join() puts them "
                "back together.",
            ], 'text = "a\\nb\\nc"\n'
               'print("\\n".join(line + "~" for line in text.splitlines()))'),
        ],
        enemy=Enemy("Agent Thompson", art.AGENT,
                    "Give us the keys, little man.",
                    "The copy is made before he reaches you."),
        riddles=[
            Riddle("What does 'w' do if the file already exists?",
                   options=("Adds at the end", "Empties it and writes "
                            "from the start", "Raises an error"),
                   answer=1, explain="'a' would append instead."),
            Riddle("What does this print?", run=True,
                   code='print("a\\nb".splitlines())',
                   options=("['a', 'b']", "['a\\nb']", "('a', 'b')"),
                   answer=0, explain="One string per line."),
            Riddle("What does this print?", run=True,
                   code='print("-".join(["red", "blue"]))',
                   options=("red-blue", "['red', 'blue']", "-red-blue-"),
                   answer=0, explain="join glues with the separator."),
            Riddle("The user just presses Enter at input(). What do you "
                   "get?", run=True,
                   code='answer = ""   # what input() returns\n'
                        'print(answer == "", not answer)',
                   options=("True True", "False False"), answer=0,
                   explain="An empty string, which is falsy."),
        ],
        trial=TRIAL_1,
        victory=[Line(KEYMAKER, "Two keys now. One for you, one for "
                      "Zion.")],
    ),
    Chapter(
        id="w4c2",
        title="The Three Channels",
        exercise="ex2 · ft_stream_management.py",
        concept="sys.stdin · sys.stdout · sys.stderr",
        story=[
            Line("The Merovingian", "Three channels run through my house, "
                 "older than the Internet itself."),
            Line(KEYMAKER, "In: stdin. Out: stdout. Bad news: stderr. Keep "
                 "them apart, and the operators can filter what they "
                 "need."),
        ],
        pages=[
            Page("Three streams", [
                "sys.stdout: normal output (print writes there). "
                "sys.stderr: error messages. sys.stdin: input.",
                "Separate channels let users redirect them: "
                "python3 x.py > out.txt still shows errors on screen.",
            ], 'import sys\n\n'
               'sys.stdout.write("normal output\\n")\n'
               'sys.stderr.write("[STDERR] something went wrong\\n")\n'
               'print("also an error", file=sys.stderr)'),
            Page("Input without input()", [
                "input() is a shortcut: write a prompt, read a line. You "
                "can do it by hand: sys.stdout.write(prompt), "
                "sys.stdout.flush() so it shows now, then "
                "sys.stdin.readline() - which keeps the \\n.",
            ], 'import sys\n\n'
               'sys.stdout.write("Name: ")\n'
               'sys.stdout.flush()\n'
               'name = sys.stdin.readline().strip()\n'
               'print(f"Hello {name}")'),
        ],
        enemy=Enemy("the Merovingian's Operators", art.TWINS,
                    "Cause and effect, Neo. Output and error.",
                    "Each message flows on its own channel. The "
                    "Merovingian's men lose the thread."),
        riddles=[
            Riddle("You run  python3 x.py > out.txt .  Where do sys.stderr "
                   "messages go?",
                   options=("Into out.txt", "Still to the screen: > only "
                            "redirects stdout"),
                   answer=1, explain="That's why errors have their own "
                                     "channel."),
            Riddle("What does sys.stdin.readline() return for the input "
                   "'neo' + Enter?",
                   options=("'neo'", "'neo\\n'"), answer=1,
                   explain="It keeps the new line: .strip() it."),
            Riddle("Why sys.stdout.flush() after writing a prompt?",
                   options=("To clear the screen",
                            "Output is buffered: flush makes the prompt "
                            "appear right away"),
                   answer=1, explain="Otherwise the prompt may show late."),
            Riddle("Fill the blank:  print(\"oops\", file=sys.______)",
                   kind="blank", answer=("stderr",),
                   explain="print can write to any stream."),
        ],
        trial=TRIAL_2,
        victory=[Line(KEYMAKER, "Clean channels. The operators can hear "
                      "you.")],
    ),
    Chapter(
        id="w4c3",
        title="The Vault",
        exercise="ex3 · ft_vault_security.py",
        concept="the with statement · context managers",
        story=[
            Line(KEYMAKER, "Behind the last door is a vault that closes "
                 "itself. Always. Even if you're shot on the way out."),
            Line(KEYMAKER, "In Python it is called with."),
        ],
        pages=[
            Page("with", [
                "with open(name) as file: opens the file, runs the block, "
                "and closes the file when the block ends - normally, by "
                "return, or by an exception. It's try/finally built in.",
            ], 'with open("vault.txt", "w") as file:\n'
               '    file.write("Neo was here\\n")\n'
               'print(file.closed)'),
            Page("Returning a status", [
                "A function can return a tuple: (succeeded, details). The "
                "caller unpacks it and decides what to do.",
            ], 'def safe_read(name: str) -> tuple[bool, str]:\n'
               '    try:\n'
               '        with open(name) as file:\n'
               '            return (True, file.read())\n'
               '    except OSError as e:\n'
               '        return (False, str(e))\n'
               '\n'
               '\n'
               'print(safe_read("/no/such/file"))'),
        ],
        enemy=Enemy("the Architect's Firewall", art.ARCHITECT,
                    "No file left open. No exception unhandled. Prove it.",
                    "The vault closes by itself. The firewall lets you "
                    "through."),
        riddles=[
            Riddle("What does this print?", run=True,
                   code='with open("v.txt", "w") as file:\n'
                        '    file.write("x")\nprint(file.closed)',
                   options=("True", "False"), answer=0,
                   explain="Leaving the with block closed the file."),
            Riddle("And when an exception flies out of the block?", run=True,
                   code='try:\n    with open("v.txt", "w") as file:\n'
                        '        raise ValueError("Agent!")\n'
                        'except ValueError:\n    pass\nprint(file.closed)',
                   options=("True", "False"), answer=0,
                   explain="Closed anyway - like a finally."),
            Riddle("What does this print?", run=True,
                   code='ok, text = (False, "door locked")\n'
                        'print(ok, text)',
                   options=("False door locked",
                            "(False, 'door locked')"), answer=0,
                   explain="The tuple was unpacked into two names."),
            Riddle("with open(...) is a shortcut for which pattern?",
                   options=("try / finally: file.close()",
                            "if / else", "a for loop"),
                   answer=0, explain="That's a context manager."),
        ],
        trial=TRIAL_3,
        victory=[Line(KEYMAKER, "You have all the keys now, Neo. Go.")],
    ),
]

FILES = {"ancient_fragment.txt": FRAGMENT}
IO = {"print", "len", "open", "str", "int", "float", "list", "dict", "set",
      "tuple"}

EXERCISES = [
    Exercise("ex0", "ft_ancient_text.py",
             ["Read the file given as argument, display it like cat.",
              "Handle missing/inaccessible files."],
             IO, needs=["sys.argv", "close"], forbid=["with"],
             runs=[Run(expect=["Usage"]),
                   Run(["foo"], expect=["Errno 2"]),
                   Run(["ancient_fragment.txt"], files=FILES,
                       expect=["FRAGMENT 002", "closed"])]),
    Exercise("ex1", "ft_archive_creation.py",
             ["Add # to every line, ask a file name, save the copy."],
             IO | {"input"}, needs=["close"], forbid=["with"],
             runs=[Run(["ancient_fragment.txt"], stdin="\n", files=FILES,
                       expect=["2087#", "Not saving"]),
                   Run(["ancient_fragment.txt"], stdin="new.txt\n",
                       files=FILES, expect=["saved"])]),
    Exercise("ex2", "ft_stream_management.py",
             ["Errors on sys.stderr with [STDERR], input via sys.stdin."],
             IO, needs=["sys.stdin", "sys.stderr"],
             forbid=["with", "input()"],
             runs=[Run(["foo"], expect_err=["[STDERR]"]),
                   Run(["ancient_fragment.txt"], stdin="\n", files=FILES,
                       expect=["2087#"])]),
    Exercise("ex3", "ft_vault_security.py",
             ["secure_archive(name, action, content) -> (bool, str), "
              "using with."],
             {"open", "print", "str", "int", "float", "list", "dict", "set",
              "tuple"},
             functions=["secure_archive"], needs=["with"],
             runs=[Run(files=FILES, expect=["True", "False"])]),
]

WORLD = World(
    id="w4",
    title="The Keymaker",
    project="Data Archivist",
    subtitle="Files and streams",
    mentor=KEYMAKER,
    intro=[
        Line("Morpheus", "The Keymaker. The Merovingian keeps him "
             "prisoner. Without him, we can't reach the Source."),
        Line(KEYMAKER, "Doors, Neo. Files. Open them, read them, write "
             "them... and close them. Always close them."),
    ],
    chapters=CHAPTERS,
    defense=[
        Riddle("Evaluator: 'What does open() return?'",
               options=("The file's text",
                        "A file object (typing.IO) you read/write through"),
               answer=1, explain="read() gives the text."),
        Riddle("Evaluator: 'Why separate stdout and stderr?'",
               options=("Colours",
                        "So errors can be redirected or filtered "
                        "separately from normal output"),
               answer=1, explain="> out.txt still shows the errors."),
        Riddle("Evaluator: 'What does with do that open/close doesn't?'",
               options=("Nothing",
                        "It closes the file automatically when the block "
                        "ends, even if an exception happens"),
               answer=1, explain="A context manager: try/finally built in."),
        Riddle("Evaluator: 'Why is your function returning a tuple?'",
               options=("The subject says so, and it lets the caller know "
                        "BOTH whether it worked and the content/error",
                        "Tuples are faster"),
               answer=0, explain="(True|False, str)."),
    ],
    boss=Enemy("the Merovingian", art.AGENT,
               "You think you can just walk out with my Keymaker?",
               "Every file closed, every error on its channel. The "
               "Merovingian has nothing to hold you with."),
    exercises=EXERCISES,
    outro=[Line(KEYMAKER, "This door leads to the Source."),
           Line("The Oracle", "Everything that has a beginning has an end,"
                " Neo.")],
)
