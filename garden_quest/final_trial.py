"""The Final Trial: check YOUR real Garden Guardian project.

The game never writes the exercises for you. Instead it reads the files
you wrote (ex0/ft_first_exception.py ... ex4/ft_finally_block.py), runs
them like an evaluator would, and tells you what looks right or wrong.

Passing this check does not replace a peer evaluation: be ready to
explain every line!
"""

import ast
import builtins
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from . import ui


@dataclass
class Exercise:
    folder: str
    filename: str
    functions: list[str]
    authorized: set[str]
    expected_output: list[str]
    classes: dict[str, str] = field(default_factory=dict)
    needs: list[str] = field(default_factory=list)
    brief: list[str] = field(default_factory=list)


EXERCISES = [
    Exercise(
        "ex0", "ft_first_exception.py",
        ["input_temperature", "test_temperature"], {"int", "print"},
        ["25", "abc", "invalid literal"],
        needs=["try"],
        brief=["input_temperature(temp_str) converts and returns an int.",
               "test_temperature() tries '25' and 'abc' and survives."],
    ),
    Exercise(
        "ex1", "ft_raise_exception.py",
        ["input_temperature", "test_temperature"], {"int", "print"},
        ["25", "abc", "100", "-50"],
        needs=["try", "raise"],
        brief=["Same as ex0, plus: raise if not 0..40 (limits included).",
               "Also test '100' and '-50'."],
    ),
    Exercise(
        "ex2", "ft_different_errors.py",
        ["garden_operations", "test_error_types"], {"print", "open", "int"},
        ["ValueError", "ZeroDivisionError", "FileNotFoundError",
         "TypeError"],
        needs=["try"],
        brief=["garden_operations(operation_number): 0..3 run faulty code "
               "(Value/ZeroDivision/FileNotFound/TypeError).",
               "test_error_types() catches each one, without type()."],
    ),
    Exercise(
        "ex3", "ft_custom_errors.py", [], {"print"},
        ["PlantError", "WaterError", "GardenError"],
        classes={"GardenError": "Exception", "PlantError": "GardenError",
                 "WaterError": "GardenError"},
        needs=["try", "raise"],
        brief=["GardenError(Exception), PlantError and WaterError "
               "(GardenError), each with a default message.",
               "Functions raising them, catching them, and catching all "
               "with GardenError."],
    ),
    Exercise(
        "ex4", "ft_finally_block.py",
        ["water_plant", "test_watering_system"], {"print", "capitalize"},
        ["Opening", "Closing", "PlantError"],
        classes={"PlantError": ""},
        needs=["try", "raise", "finally"],
        brief=["water_plant(plant_name): OK if capitalized, else raise "
               "PlantError.",
               "test_watering_system(): open, water, stop at first error, "
               "ALWAYS close in finally."],
    ),
]

KEYWORD_NODES = {"try": ast.Try, "raise": ast.Raise}


@dataclass
class Report:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _static_checks(exercise: Exercise, tree: ast.Module,
                   report: Report) -> None:
    functions = {node.name: node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef)}
    classes = {node.name: node for node in ast.walk(tree)
               if isinstance(node, ast.ClassDef)}
    for name in exercise.functions:
        if name in functions:
            report.passed.append(f"function {name}() exists")
        else:
            report.failed.append(f"function {name}() is missing")
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
    for keyword in exercise.needs:
        if keyword == "finally":
            found = any(isinstance(node, ast.Try) and node.finalbody
                        for node in ast.walk(tree))
        else:
            found = any(isinstance(node, KEYWORD_NODES[keyword])
                        for node in ast.walk(tree))
        if found:
            report.passed.append(f"uses `{keyword}`")
        else:
            report.failed.append(f"`{keyword}` is never used")
    for function in functions.values():
        args = function.args.args + function.args.kwonlyargs
        missing = [arg.arg for arg in args
                   if arg.annotation is None and arg.arg != "self"]
        if function.returns is None or missing:
            report.failed.append(f"{function.name}() is missing type hints")
    if exercise.folder == "ex2":
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func,
                                                         ast.Name):
                if node.func.id == "type":
                    report.failed.append("type() is used (forbidden)")
    _authorized(exercise, tree, classes, functions, report)


def _authorized(exercise: Exercise, tree: ast.Module,
                classes: dict[str, ast.ClassDef],
                functions: dict[str, ast.FunctionDef],
                report: Report) -> None:
    """List builtin functions used that the subject didn't authorize."""
    used = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name in classes or name in functions:
                continue
            value = getattr(builtins, name, None)
            if isinstance(value, type) and issubclass(value, BaseException):
                continue
            if value is not None and name not in exercise.authorized:
                used.add(name)
        elif isinstance(node.func, ast.Attribute):
            attribute = node.func.attr
            if attribute == "capitalize":
                continue
            if attribute not in ("__init__",) and attribute in dir(str):
                used.add(f".{attribute}()")
    if used:
        report.notes.append(
            "not in the authorized list: " + ", ".join(sorted(used))
            + " - double check the subject / ask your peers")


def _run(path: Path, report: Report, expected: list[str]) -> None:
    try:
        done = subprocess.run([sys.executable, path.name], cwd=path.parent,
                              capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        report.failed.append("program runs for more than 10 seconds")
        return
    if done.returncode != 0 or "Traceback" in done.stderr:
        last = (done.stderr.strip().splitlines() or ["?"])[-1]
        report.failed.append(f"the program CRASHED: {last}")
        return
    report.passed.append("runs without crashing")
    if not done.stdout.strip():
        report.failed.append("prints nothing (did you call the test in "
                             "the main part?)")
        return
    missing = [word for word in expected
               if word.lower() not in done.stdout.lower()]
    if missing:
        report.failed.append("the output never mentions: "
                             + ", ".join(missing))
    else:
        report.passed.append("output covers every case of the subject")
    if path.parent.name == "ex4":
        lines = [line for line in done.stdout.splitlines() if line.strip()]
        closes = [line for line in lines if "clos" in line.lower()]
        opens = [line for line in lines if "open" in line.lower()]
        if len(closes) < len(opens):
            report.failed.append(f"opened {len(opens)} times but closed "
                                 f"only {len(closes)} times")


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
            remarks = "; ".join(line.split(":", 1)[-1] for line in first)
            report.notes.append(f"{tool} remarks: {remarks}")


def check_exercise(root: Path, exercise: Exercise) -> Report:
    report = Report()
    path = root / exercise.folder / exercise.filename
    if not path.exists():
        report.failed.append(f"{exercise.folder}/{exercise.filename} does "
                             "not exist yet")
        return report
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as error:
        report.failed.append(f"SyntaxError line {error.lineno}: "
                             f"{error.msg}")
        return report
    _static_checks(exercise, tree, report)
    _run(path, report, exercise.expected_output)
    _lint(path, report)
    return report


def show_briefing() -> None:
    ui.title("📜 The Real Garden: your project")
    for exercise in EXERCISES:
        ui.say(f"  {exercise.folder}/{exercise.filename}", "yellow",
               slow=False)
        for line in exercise.brief:
            print("     " + line)
    print()
    ui.say("  Rules from the subject: Python 3.10+, flake8 clean, type "
           "hints everywhere (mypy),", slow=False)
    ui.say("  one file per exercise, programs must NEVER crash, only "
           "authorized functions.", slow=False)


def run_final_trial(root: Path) -> bool:
    """Check all five exercises. Returns True if everything passed."""
    ui.title("⚖  The Final Trial")
    ui.say(f"  Checking the project in {root}", "grey", slow=False)
    print()
    all_good = True
    for exercise in EXERCISES:
        report = check_exercise(root, exercise)
        ok = not report.failed
        all_good = all_good and ok
        mark = ui.paint("✓", "green") if ok else ui.paint("✗", "red")
        print(f"  {mark} {ui.paint(exercise.folder, 'bold')}/"
              f"{exercise.filename}")
        for line in report.passed:
            print("      " + ui.paint("✓ " + line, "green"))
        for line in report.failed:
            print("      " + ui.paint("✗ " + line, "red"))
        for line in report.notes:
            print("      " + ui.paint("• " + line, "yellow"))
    print()
    if all_good:
        ui.say("  All five exercises pass the trial! Now make sure you can "
               "EXPLAIN them to a peer.", "green")
    else:
        ui.say("  Some trials remain. Fix them and run the check again - "
               "the Blight is patient, but so are you.", "yellow")
    return all_good
