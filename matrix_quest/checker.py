"""The real-project checker: reads YOUR exercise files and tests them.

The game never writes the exercises for you. It reads the files you
wrote (ex0/..., ex1/...), runs them like an evaluator would, and tells
you what looks right or wrong. It doesn't replace a peer evaluation:
be ready to explain every line!
"""

import ast
import builtins
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

from .forge import has_main_guard
from .model import Exercise, Run


def _any(tree: ast.Module, kind: type) -> bool:
    return any(isinstance(node, kind) for node in ast.walk(tree))


def _calls(tree: ast.Module, dotted: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if ast.unparse(node.func) == dotted:
                return True
    return False


def _mentions(tree: ast.Module, dotted: str) -> bool:
    return any(isinstance(node, ast.Attribute)
               and ast.unparse(node) == dotted for node in ast.walk(tree))


def _decorated(tree: ast.Module, name: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if any(ast.unparse(d) == name for d in node.decorator_list):
                return True
    return _calls(tree, name)


def _nested_class(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any(isinstance(child, ast.ClassDef) for child in node.body):
                return True
    return False


def _finally(tree: ast.Module) -> bool:
    return any(isinstance(node, ast.Try) and bool(node.finalbody)
               for node in ast.walk(tree))


def _protected(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and ast.unparse(node.value) == \
                "self" and node.attr.startswith("_") and \
                not node.attr.startswith("__"):
            return True
    return False


def _mangled(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr.startswith("__") \
                and not node.attr.endswith("__"):
            return True
    return False


FEATURES: dict[str, tuple[str, Callable[[ast.Module], bool]]] = {
    "try": ("try/except", lambda t: _any(t, ast.Try)),
    "raise": ("raise", lambda t: _any(t, ast.Raise)),
    "finally": ("finally", _finally),
    "class": ("a class", lambda t: _any(t, ast.ClassDef)),
    "main_guard": ('if __name__ == "__main__":', has_main_guard),
    "with": ("the with statement", lambda t: _any(t, ast.With)),
    "yield": ("yield (a generator)", lambda t: _any(t, ast.Yield)),
    "listcomp": ("a list comprehension", lambda t: _any(t, ast.ListComp)),
    "dictcomp": ("a dict comprehension", lambda t: _any(t, ast.DictComp)),
    "super": ("super()", lambda t: _calls(t, "super")),
    "staticmethod": ("a static method",
                     lambda t: _decorated(t, "staticmethod")),
    "classmethod": ("a class method",
                    lambda t: _decorated(t, "classmethod")),
    "nested_class": ("a nested class", _nested_class),
    "protected": ("protected attributes (self._x)", _protected),
    "mangled": ("name mangling (self.__x)", _mangled),
    "type()": ("type()", lambda t: _calls(t, "type")),
    "input()": ("input()", lambda t: _calls(t, "input")),
    "sys.argv": ("sys.argv", lambda t: _mentions(t, "sys.argv")),
    "sys.stdin": ("sys.stdin", lambda t: _mentions(t, "sys.stdin")),
    "sys.stderr": ("sys.stderr", lambda t: "sys.stderr" in ast.unparse(t)),
    "math.sqrt": ("math.sqrt()", lambda t: _calls(t, "math.sqrt")),
    "close": (".close()", lambda t: any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "close" for n in ast.walk(t))),
}


class Report:
    def __init__(self, exercise: Exercise) -> None:
        self.exercise = exercise
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.notes: list[str] = []

    def as_dict(self) -> dict[str, object]:
        return {"folder": self.exercise.folder,
                "file": self.exercise.filename,
                "brief": self.exercise.brief,
                "ok": not self.failed, "passed": self.passed,
                "failed": self.failed, "notes": self.notes}


def _structure(exercise: Exercise, tree: ast.Module, report: Report) -> None:
    functions = {node.name: node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef)}
    classes = {node.name: node for node in ast.walk(tree)
               if isinstance(node, ast.ClassDef)}
    for name in exercise.functions:
        if name in functions:
            report.passed.append(f"{name}() exists")
        else:
            report.failed.append(f"{name}() is missing")
    for name, parent in exercise.classes.items():
        if name not in classes:
            report.failed.append(f"class {name} is missing")
            continue
        bases = [ast.unparse(base) for base in classes[name].bases]
        if parent and parent not in bases:
            report.failed.append(f"class {name} should inherit from "
                                 f"{parent} (found: {bases or 'nothing'})")
        else:
            report.passed.append(f"class {name} is defined")
    for key in exercise.needs:
        label, test = FEATURES[key]
        if test(tree):
            report.passed.append(f"uses {label}")
        else:
            report.failed.append(f"{label} is never used")
    for key in exercise.forbid:
        label, test = FEATURES[key]
        if test(tree):
            report.failed.append(f"{label} is used, but not allowed here")
    for function in functions.values():
        args = function.args.args + function.args.kwonlyargs
        missing = [arg.arg for arg in args
                   if arg.annotation is None and arg.arg not in
                   ("self", "cls")]
        if function.returns is None or missing:
            report.failed.append(f"{function.name}() is missing type hints")
    _authorized(exercise, tree, set(functions) | set(classes), report)


def _authorized(exercise: Exercise, tree: ast.Module, own: set[str],
                report: Report) -> None:
    """List builtin functions used that the subject didn't authorize."""
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name in own:
                continue
            value = getattr(builtins, name, None)
            if isinstance(value, type) and issubclass(value, BaseException):
                continue
            if value is not None and name not in exercise.authorized:
                used.add(name + "()")
    if used:
        report.notes.append("not in the authorized list: "
                            + ", ".join(sorted(used))
                            + " - double check the subject with a peer")


def _execute(path: Path, run: Run, report: Report) -> None:
    label = " ".join(["python3", path.name] + run.args)
    if run.stdin:
        typed = run.stdin.strip().replace("\n", " / ") or "Enter"
        label += f" <<< {typed}"
    with tempfile.TemporaryDirectory() as folder:
        for name, content in run.files.items():
            (Path(folder) / name).write_text(content)
        try:
            done = subprocess.run([sys.executable, str(path)] + run.args,
                                  input=run.stdin, capture_output=True,
                                  text=True, timeout=10, cwd=folder)
        except subprocess.TimeoutExpired:
            report.failed.append(f"`{label}` runs for more than 10 s")
            return
    if done.returncode != 0 or "Traceback" in done.stderr:
        last = (done.stderr.strip().splitlines() or ["?"])[-1]
        report.failed.append(f"`{label}` CRASHED: {last}")
        return
    missing = [w for w in run.expect if w.lower() not in done.stdout.lower()]
    missing += [f"{w} (on stderr)" for w in run.expect_err
                if w.lower() not in done.stderr.lower()]
    if missing:
        report.failed.append(f"`{label}` output never shows: "
                             + ", ".join(missing))
    else:
        report.passed.append(f"`{label}` runs fine")


def _lint(path: Path, report: Report) -> None:
    for tool in ("flake8", "mypy"):
        if shutil.which(tool) is None:
            report.notes.append(f"{tool} is not installed (pip install "
                                f"{tool}) - the subject requires it")
            continue
        done = subprocess.run([tool, str(path)], capture_output=True,
                              text=True, timeout=60)
        if done.returncode == 0:
            report.passed.append(f"{tool} is clean")
        else:
            first = done.stdout.strip().splitlines()[:3]
            report.failed.append(f"{tool}: " + " | ".join(
                line.split(":", 1)[-1].strip() for line in first))


def check_exercise(root: Path, exercise: Exercise) -> Report:
    report = Report(exercise)
    path = root / exercise.folder / exercise.filename
    if not path.exists():
        report.failed.append(f"{exercise.folder}/{exercise.filename} "
                             "does not exist yet")
        return report
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as error:
        report.failed.append(f"SyntaxError line {error.lineno}: {error.msg}")
        return report
    _structure(exercise, tree, report)
    for run in exercise.runs or [Run()]:
        _execute(path, run, report)
    _lint(path, report)
    return report


def check_project(root: Path, exercises: list[Exercise]) -> list[Report]:
    return [check_exercise(root, exercise) for exercise in exercises]
