"""The Crystal Ball runs a snippet with real Python and shows what happened.

This is how the game proves that its answers are not made up: every code
riddle you meet can be replayed here, exactly as Python would run it.
"""

import contextlib
import io
import traceback


def run_snippet(code: str) -> str:
    """Execute code and return everything it printed.

    If the code crashes, the last line of the traceback is added, just like
    the last line you would see in your terminal.
    """
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            exec(code, {"__name__": "__main__"})
        except Exception:
            lines = traceback.format_exc().strip().splitlines()
            print("💥 CRASH → " + lines[-1])
    return output.getvalue().rstrip("\n")
