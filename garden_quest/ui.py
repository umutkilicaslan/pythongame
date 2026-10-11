"""Terminal helpers: colours, slow text, prompts and little drawings."""

import os
import sys
import time

_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
SPEED = 0.012  # seconds per character, set to 0 with --fast

CODES = {
    "green": "32", "red": "31", "yellow": "33", "blue": "34",
    "magenta": "35", "cyan": "36", "grey": "90", "bold": "1",
}


class QuitGame(Exception):
    """Raised when the player types 'quit' at any prompt."""


def paint(text: str, color: str) -> str:
    """Wrap text in an ANSI colour code (if the terminal supports it)."""
    if not _COLOR:
        return text
    return f"\033[{CODES[color]}m{text}\033[0m"


def say(text: str = "", color: str = "", slow: bool = True) -> None:
    """Print text, optionally with a typewriter effect."""
    if not slow or SPEED <= 0 or not sys.stdout.isatty():
        print(paint(text, color) if color else text)
        return
    if color and _COLOR:
        sys.stdout.write(f"\033[{CODES[color]}m")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(SPEED)
    print("\033[0m" if color and _COLOR else "")


def narrate(lines: list[str]) -> None:
    """Tell a bit of story, one paragraph at a time."""
    for line in lines:
        say(line, "cyan")
    print()


def code_block(code: str) -> None:
    """Show a code snippet inside a scroll-like frame."""
    lines = code.strip("\n").splitlines()
    width = max([len(line) for line in lines] + [30]) + 2
    print(paint("  ┌" + "─" * width + "┐", "grey"))
    for line in lines:
        print(paint("  │ ", "grey") + paint(line.ljust(width - 1), "yellow")
              + paint("│", "grey"))
    print(paint("  └" + "─" * width + "┘", "grey"))


def ask(prompt: str, keep_indent: bool = False) -> str:
    """Read one line from the player. 'quit' leaves the game."""
    try:
        answer = input(paint(prompt, "bold")).rstrip()
    except EOFError:
        raise QuitGame()
    if answer.strip().lower() in ("quit", "exit"):
        raise QuitGame()
    return answer if keep_indent else answer.strip()


def pause(message: str = "  [press Enter to continue] ") -> None:
    ask(paint(message, "grey"))


def choose(prompt: str, options: list[str]) -> int:
    """Show a numbered menu and return the chosen index."""
    for number, option in enumerate(options, start=1):
        print(f"   {paint(str(number), 'magenta')}) {option}")
    while True:
        answer = ask(prompt)
        try:
            index = int(answer) - 1
            if 0 <= index < len(options):
                return index
        except ValueError:
            pass
        say(f"  Please type a number between 1 and {len(options)}.",
            "grey", slow=False)


def bar(current: int, maximum: int, color: str, symbol: str = "♥") -> str:
    """Draw a health bar such as ♥♥♥♡♡."""
    full = symbol * max(current, 0)
    empty = "♡" * max(maximum - current, 0)
    return paint(full, color) + paint(empty, "grey")


def title(text: str) -> None:
    line = "═" * (len(text) + 4)
    print()
    print(paint(f"╔{line}╗", "green"))
    print(paint(f"║  {text}  ║", "green"))
    print(paint(f"╚{line}╝", "green"))
    print()


BANNER = r"""
        _.-.                                 .-._
      ,'/ //\      G A R D E N   Q U E S T  /\\ \`.
     /// // /)    ~ the Exception Grimoire ~ (\ \\ \\\
    /// // //|                               |\\ \\ \\\
   ///_//_//_|    🌱  try   🔥 raise         |_\\_\\_\\\
                  🐍 except 🛡  finally
"""
