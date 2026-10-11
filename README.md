# 🌱 Garden Quest — the Exception Grimoire

A terminal RPG that teaches the **Garden Guardian** project (Python
exception handling: `try`, `except`, `raise`, custom errors, `finally`).

The Chaos Blight is corrupting the sensors of the Enchanted Greenhouse.
To save it, you learn one spell per chapter. Each chapter is one exercise
of the subject:

| Chapter | Monster | Spell | Subject exercise |
|---|---|---|---|
| 0. The Whispering Thermometer | Garbled Gremlin | `try` / `except` | ex0 `ft_first_exception.py` |
| 1. The Ember Drake | Ember Drake | `raise` | ex1 `ft_raise_exception.py` |
| 2. The Hydra of Many Heads | Hydra | many `except` clauses | ex2 `ft_different_errors.py` |
| 3. The Mimic Seeds | Mimic Seedling | your own exception classes | ex3 `ft_custom_errors.py` |
| 4. The Eternal Fountain | Flood Serpent | `finally` | ex4 `ft_finally_block.py` |
| 5. The Garden Guardian | Murphy the Blight King | defense questions + **your real project** | all |

## How to play

```bash
python3 play.py          # start or continue (needs Python 3.10+)
python3 play.py --fast   # no typewriter effect
python3 play.py --reset  # start over
```

Type `quit` at any prompt to save and leave. Progress is saved automatically.

Each chapter has three parts:

1. **📖 The Grimoire** – short lessons with examples.
2. **⚔ The battle** – code riddles ("what does this print?", "fill the
   blank"). A right answer hits the monster, a wrong one costs a heart and
   the riddle comes back later. After each answer the **🔮 Crystal Ball**
   runs the code with real Python, so you see what actually happens.
3. **⚒ The Spell Forge** – you write real code. The game creates a file in
   `workshop/` with a skeleton, you fill it in with your own editor, and the
   forge tests it (and runs flake8 / mypy if they are installed). The forge
   trials are the subject's exercises *in disguise* (mana instead of
   temperature, potions instead of plants), so you practise the idea without
   copying an answer.

In the **finale** you answer the questions a peer might ask at your defense,
then write the real `ex0/`…`ex4/` files yourself. The **Final Trial** checks
them like an evaluator would: files and function names, type hints, `try` /
`raise` / `finally`, no `type()` in ex2, the program never crashes, the
output covers every case, flake8 and mypy.

You can also run that check anytime, outside the game:

```bash
python3 play.py --check /path/to/your/project
```

The **🔮 Crystal Ball sandbox** in the main menu lets you type any Python
and see what it does — perfect for "what if I…" experiments.

```bash
pip install flake8 mypy   # recommended: the subject requires both
```

## Peek behind the curtain

The game itself is written with the spells it teaches. Once you know them,
look at the code:

- `garden_quest/battle.py` defines a custom `HeroFainted` exception and
  *raises* it when you run out of hearts; `garden_quest/game.py` *catches*
  it so the game never crashes.
- `garden_quest/forge.py` raises `ForgeFailure` from each check and catches
  it to show you a friendly message.
- `garden_quest/hero.py` catches `FileNotFoundError` and
  `json.JSONDecodeError` separately when loading your save.
- `garden_quest/game.py` saves your progress in a `finally:` block, so
  even quitting with Ctrl+C keeps your progress.
