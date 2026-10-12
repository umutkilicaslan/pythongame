"""Run Python code in a separate process and collect what it printed.

This is Tank's operator console: it proves the game's answers are real by
running every code riddle with the same Python you use for your projects.
"""

import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Output:
    stdout: str
    stderr: str
    code: int
    timeout: bool = False

    def as_dict(self) -> dict[str, object]:
        return {"stdout": self.stdout, "stderr": self.stderr,
                "code": self.code, "timeout": self.timeout}


def short_error(stderr: str) -> str:
    """Keep only the last line of a traceback, like a quick glance."""
    if "Traceback" not in stderr:
        return stderr
    return stderr.strip().splitlines()[-1]


def run_file(path: Path, args: str = "", stdin: str = "",
             cwd: Path | None = None, timeout: int = 10) -> Output:
    try:
        argv = shlex.split(args)
    except ValueError as error:
        return Output("", f"Could not read the arguments: {error}", 1)
    try:
        done = subprocess.run([sys.executable, str(path)] + argv,
                              input=stdin, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd or path.parent)
    except subprocess.TimeoutExpired:
        return Output("", f"Stopped after {timeout} seconds (infinite loop, "
                      "or waiting for input you didn't give?)", 1, True)
    return Output(done.stdout, done.stderr, done.returncode)


def run_code(code: str, args: str = "", stdin: str = "",
             cwd: Path | None = None) -> Output:
    """Run a snippet as if it were a file called snippet.py."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "snippet.py"
        path.write_text(code)
        result = run_file(path, args, stdin, cwd or Path(folder))
    result.stderr = result.stderr.replace(str(path), "snippet.py")
    return result
