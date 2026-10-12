# MATRIX//QUEST

*Wake up, Neo... The Matrix has you.*

A browser RPG where **you are Neo** and learn the four Python projects of the
curriculum. Every chapter is one exercise of a subject. You meet the crew, train
with short lessons, fight code riddles that **real Python** checks, then **forge**
the code yourself. At the end of each world, the game checks **your real
project** (`ex0/`, `ex1/`, ...).

| World | Mentor | Project | What you learn | Chapters |
|---|---|---|---|---|
| 1. The Construct | Morpheus | Code Cultivation | `__main__`, classes, methods, `__init__`, encapsulation, inheritance, static/class methods, nested classes | 7 |
| 2. Agent Protocols | Trinity | Garden Guardian | `try`/`except`, `raise`, error types, custom exceptions, `finally` | 5 |
| 3. The Oracle | The Oracle | Data Quest | `sys.argv`, lists, tuples, sets, dicts, generators, comprehensions | 7 |
| 4. The Keymaker | The Keymaker | Data Archivist | `open`/`read`/`write`/`close`, stdin/stdout/stderr, `with` | 4 |

## Play

```bash
python3 play.py
```

That's all: it starts a small local server and opens the game in your
browser (Python 3.10+, no packages needed). If the browser doesn't open, go
to the address printed in the terminal. Press `Ctrl+C` in the terminal to stop.

```bash
pip install flake8 mypy                # recommended: the subjects require both
python3 play.py --no-browser           # only print the address
python3 play.py --reset                # forget your progress
python3 play.py --check w2 ~/my-repo   # check a real project in the terminal
```

## How a chapter works

1. **Briefing**: the crew explains the mission (story).
2. **Training**: 2–4 short lessons with examples. Click **▶ Try it** to open any
   example in the Construct and run it.
3. **Fight**: code riddles like "What does this print?" or "Fill in the blank".
   A right answer hits the enemy; a wrong one costs a heart and the riddle comes
   back later. After each answer, **Tank's console** shows what real Python
   printed.
4. **Forge**: you write a real file in `workshop/`, in the built-in editor or
   in your own (VS Code, vim...; press **↻ Reload file** after editing outside).
   **▶ Run** runs it with the arguments and input you choose. **✔ Test my code**
   runs the trials and tells you exactly what is wrong. Once everything passes,
   flake8 and mypy also run.

The forge trials are the subject's exercises **in disguise**: a `Program` class
instead of `Plant`, signals instead of temperatures, an armory instead of an
inventory... You practise the idea without copying an answer.

**Final test** of each world: the evaluators' questions (a boss fight), then the
project checker reads the folder that holds your `ex0/`, `ex1/`... It runs every
exercise like an evaluator would and lists what passes, what fails, and which
functions are not on the authorized list. It never writes your exercises for
you, and it doesn't replace a peer evaluation: be ready to explain every line.

## Easy to read

Open **⚙ Settings** to change:

- the text size (4 sizes)
- the theme: Matrix (black and green), Calm dark, or Light
- the digital rain in the background (on or off)
- the typewriter effect for dialogue (on or off)

It also works on a phone-sized window. Keyboard shortcuts:

- <kbd>Enter</kbd> continues the dialogue
- <kbd>1</kbd>–<kbd>4</kbd> answer a riddle
- <kbd>Ctrl</kbd>+<kbd>S</kbd> saves in the forge
- <kbd>Ctrl</kbd>+<kbd>Enter</kbd> tests in the forge, or runs in the Construct

## Under the hood

```
play.py                  starts the server (or --check in the terminal)
matrix_quest/
  server.py              local HTTP server + JSON API for the browser
  harness.py             runs a trial's checks in a separate Python process
  forge.py               helpers the checks use (call, script, need...)
  checker.py             the real-project checker
  runner.py              runs code snippets (Tank's console, the Construct)
  progress.py            your save file (.matrix_save.json)
  model.py               dataclasses: World, Chapter, Riddle, Trial...
  worlds/                the content: one file per project
web/                     the browser UI (HTML/CSS/JS, CodeMirror bundled)
```

Your code always runs in a **separate process** with a time limit, so an
infinite loop or a crash can't break the game. The server only listens on
`127.0.0.1`, and every request that runs code must carry a secret token that
only the page served by the game knows.

The game uses what it teaches. `harness.py` and `forge.py` raise and catch
their own `ForgeFailure` exception. `server.py` turns a `BadRequest` exception
into an HTTP error. `play.py` closes the server in a `finally:` block. The
content in `worlds/` is built from dataclasses, lists and dicts.
