"""Tools used by the trial checks to test the code you write.

Each check *raises* ForgeFailure when something is wrong; the harness
*catches* it and shows you the message. The checks never run inside the
game server itself: harness.py runs them in a separate Python process,
so an infinite loop or a crash in your code can't break the game.
"""

import ast
import contextlib
import importlib.util
import io
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


class ForgeFailure(Exception):
    """Raised by a check when the player's code does not pass it."""


@dataclass
class Spell:
    """Everything a check may look at."""
    module: ModuleType
    source: str
    tree: ast.Module
    path: Path
    tmp: Path  # an empty folder the checks may use for files
    import_output: str = ""  # what the file printed when imported


@dataclass
class CallResult:
    value: Any
    output: str
    error: BaseException | None


@dataclass
class ScriptResult:
    stdout: str
    stderr: str
    code: int


def call(function: Callable[..., Any], *args: Any,
         stdin: str = "") -> CallResult:
    """Call a player's function, capturing prints and exceptions."""
    output = io.StringIO()
    value = None
    error: BaseException | None = None
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(output):
            try:
                value = function(*args)
            except BaseException as caught:  # SystemExit & co. too
                error = caught
    finally:
        sys.stdin = old_stdin
    return CallResult(value, output.getvalue(), error)


def script(spell: Spell, args: list[str] | None = None, stdin: str = "",
           cwd: Path | None = None) -> ScriptResult:
    """Run the player's file as a program, like `python3 file args`."""
    command = [sys.executable, str(spell.path)] + (args or [])
    try:
        done = subprocess.run(command, input=stdin, capture_output=True,
                              text=True, timeout=10, cwd=cwd or spell.tmp)
    except subprocess.TimeoutExpired:
        raise ForgeFailure("your program ran for more than 10 seconds "
                           "(infinite loop? waiting for input?)")
    return ScriptResult(done.stdout, done.stderr, done.returncode)


def no_crash(result: ScriptResult, what: str) -> None:
    if result.code != 0 or "Traceback" in result.stderr:
        last = (result.stderr.strip().splitlines() or ["?"])[-1]
        raise ForgeFailure(f"{what} crashed: {last}")


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


def has_main_guard(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            text = ast.unparse(node.test).replace("'", '"')
            if text in ('__name__ == "__main__"', '"__main__" == __name__'):
                return True
    return False


def lines(text: str) -> list[str]:
    return [line for line in text.strip().splitlines() if line.strip()]


def load(path: Path, tmp: Path) -> Spell:
    """Import the player's file. Raises ForgeFailure if it won't load."""
    source = path.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ForgeFailure(
            f"Python can't read your file (SyntaxError line {error.lineno}):"
            f" {error.msg}")
    spec = importlib.util.spec_from_file_location("player_code", path)
    if spec is None or spec.loader is None:
        raise ForgeFailure("This file can't be imported.")
    module = importlib.util.module_from_spec(spec)
    result = call(spec.loader.exec_module, module)
    if result.error is not None:
        raise ForgeFailure(
            "Your file crashed while being imported: "
            f"{type(result.error).__name__}: {result.error}")
    return Spell(module, source, tree, path, tmp, result.output)
