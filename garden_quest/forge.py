"""The Spell Forge: you write real Python, the forge tests it.

Each forge trial creates a file in the `workshop/` folder. You open it in
your own editor, write the code, save, and come back to the game. The
forge then imports your file and runs a series of trials on it.

The trials themselves are written with exceptions: each check *raises*
ForgeFailure when something is wrong, and the forge *catches* it to show
you the message instead of crashing.
"""

import ast
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from . import ui

WORKSHOP = Path(__file__).resolve().parent.parent / "workshop"


class ForgeFailure(Exception):
    """Raised by a check when the player's code does not pass it."""


@dataclass
class Spell:
    """Everything a check may look at: the module, its source and AST."""
    module: ModuleType
    source: str
    tree: ast.Module


Check = Callable[[Spell], None]


@dataclass
class ForgeTrial:
    filename: str
    mission: list[str]
    skeleton: str
    hints: list[str]
    checks: list[tuple[str, Check]] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return WORKSHOP / self.filename


# ---------------------------------------------------------------- helpers
# These are used by the checks in trials.py.

@dataclass
class CallResult:
    value: Any
    output: str
    error: BaseException | None


def call(function: Callable[..., Any], *args: Any) -> CallResult:
    """Call a player's function, capturing its prints and its exception."""
    output = io.StringIO()
    value = None
    error: BaseException | None = None
    with contextlib.redirect_stdout(output):
        try:
            value = function(*args)
        except BaseException as caught:  # we also want SystemExit & co.
            error = caught
    return CallResult(value, output.getvalue(), error)


def need(spell: Spell, name: str) -> Any:
    """Get something the player had to define, or fail politely."""
    if not hasattr(spell.module, name):
        raise ForgeFailure(f"I can't find `{name}` in your file.")
    return getattr(spell.module, name)


def uses(spell: Spell, node_type: type) -> bool:
    return any(isinstance(node, node_type) for node in ast.walk(spell.tree))


def calls_named(spell: Spell, name: str) -> bool:
    for node in ast.walk(spell.tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == name:
                return True
    return False


# ---------------------------------------------------------------- running

def _load(path: Path) -> Spell:
    """Import the player's file. Raises ForgeFailure if it won't load."""
    source = path.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ForgeFailure(
            f"Python can't read your file (SyntaxError line {error.lineno}):"
            f" {error.msg}")
    spec = importlib.util.spec_from_file_location("player_spell", path)
    if spec is None or spec.loader is None:
        raise ForgeFailure("This file can't be imported.")
    module = importlib.util.module_from_spec(spec)
    result = call(spec.loader.exec_module, module)
    if result.error is not None:
        raise ForgeFailure(
            "Your file crashed while being imported: "
            f"{type(result.error).__name__}: {result.error}")
    return Spell(module, source, tree)


def _lint(path: Path) -> None:
    """Run flake8 and mypy if they are installed (advice only)."""
    for tool in ("flake8", "mypy"):
        if shutil.which(tool) is None:
            continue
        done = subprocess.run([tool, str(path)], capture_output=True,
                              text=True, timeout=60)
        if done.returncode == 0:
            ui.say(f"   ✓ {tool} is happy", "green", slow=False)
        else:
            ui.say(f"   ⚠ {tool} has remarks (the subject requires a clean "
                   f"{tool}):", "yellow", slow=False)
            for line in done.stdout.strip().splitlines()[:8]:
                print("      " + ui.paint(line, "grey"))


def test_spell(trial: ForgeTrial) -> bool:
    """Run every check. Returns True if all passed."""
    print()
    ui.say(f"  🔨 The forge reads {trial.path.name}...", "magenta",
           slow=False)
    try:
        spell = _load(trial.path)
    except ForgeFailure as failure:
        ui.say(f"   ✗ {failure}", "red", slow=False)
        return False
    passed = 0
    for description, check in trial.checks:
        try:
            check(spell)
        except ForgeFailure as failure:
            ui.say(f"   ✗ {description}", "red", slow=False)
            ui.say(f"       → {failure}", "grey", slow=False)
        except Exception as error:
            ui.say(f"   ✗ {description}", "red", slow=False)
            ui.say(f"       → unexpected {type(error).__name__}: {error}",
                   "grey", slow=False)
        else:
            ui.say(f"   ✓ {description}", "green", slow=False)
            passed += 1
    ui.say(f"  {passed}/{len(trial.checks)} trials passed.", "bold",
           slow=False)
    if passed == len(trial.checks):
        _lint(trial.path)
        return True
    return False


def _write_skeleton(trial: ForgeTrial) -> None:
    WORKSHOP.mkdir(exist_ok=True)
    trial.path.write_text(trial.skeleton.lstrip("\n"))


def _open_editor(trial: ForgeTrial) -> None:
    editor = os.environ.get("EDITOR")
    if not editor:
        ui.say("  $EDITOR is not set. Open the file with any editor you like"
               " (VS Code, vim, nano...).", "grey", slow=False)
        return
    try:
        subprocess.run([editor, str(trial.path)])
    except OSError as error:
        ui.say(f"  Could not start {editor}: {error}", "red", slow=False)


def forge(trial: ForgeTrial) -> bool:
    """The forge menu. Returns True once the player's spell passes."""
    if not trial.path.exists():
        _write_skeleton(trial)
    ui.title("⚒  The Spell Forge")
    for line in trial.mission:
        ui.say("  " + line, slow=False)
    print()
    ui.say(f"  📄 Your file: {trial.path}", "yellow", slow=False)
    hints_seen = 0
    while True:
        print()
        options = ["Test my spell", "Get a hint", "Open in $EDITOR",
                   "Reset the file to the starting skeleton",
                   "Leave the forge (come back later)"]
        picked = ui.choose("  Forge › ", options)
        if picked == 0:
            if test_spell(trial):
                return True
        elif picked == 1:
            if hints_seen < len(trial.hints):
                hints_seen += 1
            for number in range(hints_seen):
                ui.say(f"  💡 Hint {number + 1}: {trial.hints[number]}",
                       "yellow", slow=False)
            if hints_seen == len(trial.hints):
                ui.say("  (That was the last hint. Ask a peer if you're "
                       "still stuck - that's how 42 works!)", "grey",
                       slow=False)
        elif picked == 2:
            _open_editor(trial)
        elif picked == 3:
            if ui.ask("  Erase your code? (yes/no) › ").lower() == "yes":
                _write_skeleton(trial)
                ui.say("  The file is fresh again.", "grey", slow=False)
        else:
            return False
