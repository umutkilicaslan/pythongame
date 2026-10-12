"""A tiny local web server: the browser UI talks to real Python here.

Everything stays on your machine: the server only listens on 127.0.0.1,
and every request that runs code must carry a secret token that only the
page served by this server knows.
"""

import json
import secrets
import shutil
import subprocess
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from . import progress as saves
from .checker import check_project
from .model import Chapter, Riddle, World
from .runner import run_code, run_file, short_error
from .worlds import CHAPTERS, SAMPLE_FILES, WORLDS, find_world

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
WORKSHOP = ROOT / "workshop"
HARNESS = Path(__file__).resolve().parent / "harness.py"
TYPES = {".html": "text/html", ".js": "text/javascript",
         ".css": "text/css", ".svg": "image/svg+xml"}


class BadRequest(Exception):
    """Raised when a request can't be served; becomes an HTTP 400."""


# ---------------------------------------------------------------- content

def _riddle(riddle: Riddle) -> dict[str, Any]:
    """A riddle as the browser sees it: without the answer."""
    return {"question": riddle.question, "kind": riddle.kind,
            "code": riddle.code, "options": list(riddle.options)}


def _chapter(chapter: Chapter) -> dict[str, Any]:
    trial = chapter.trial
    return {
        "id": chapter.id, "title": chapter.title,
        "exercise": chapter.exercise, "concept": chapter.concept,
        "story": [vars(line) for line in chapter.story],
        "pages": [vars(page) for page in chapter.pages],
        "enemy": vars(chapter.enemy),
        "riddles": [_riddle(riddle) for riddle in chapter.riddles],
        "victory": [vars(line) for line in chapter.victory],
        "trial": {"filename": trial.filename, "mission": trial.mission,
                  "hints": trial.hints, "checks": [name for name, _ in
                                                   trial.checks],
                  "run_args": trial.run_args, "run_stdin": trial.run_stdin},
    }


def _world(world: World) -> dict[str, Any]:
    return {
        "id": world.id, "title": world.title, "project": world.project,
        "subtitle": world.subtitle, "mentor": world.mentor,
        "intro": [vars(line) for line in world.intro],
        "outro": [vars(line) for line in world.outro],
        "chapters": [_chapter(chapter) for chapter in world.chapters],
        "defense": [_riddle(riddle) for riddle in world.defense],
        "boss": vars(world.boss),
        "exercises": [{"folder": e.folder, "file": e.filename,
                       "brief": e.brief} for e in world.exercises],
    }


def _riddles(fight: str) -> list[Riddle]:
    if fight in CHAPTERS:
        return CHAPTERS[fight].riddles
    try:
        return find_world(fight).defense
    except KeyError:
        raise BadRequest(f"unknown fight {fight!r}")


# ---------------------------------------------------------------- the game

class Game:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.progress = saves.load()
        self.lock = threading.Lock()
        WORKSHOP.mkdir(exist_ok=True)
        for name, content in SAMPLE_FILES.items():
            if not (WORKSHOP / name).exists():
                (WORKSHOP / name).write_text(content)

    def state(self) -> dict[str, Any]:
        return {"xp": self.progress.xp, "fights": self.progress.fights,
                "forged": self.progress.forged,
                "projects": self.progress.projects,
                "rank": self.progress.rank(len(WORLDS)),
                "total": len(CHAPTERS)}

    def _award(self, kind: str, item: str, xp: int) -> None:
        with self.lock:
            if self.progress.mark(kind, item, xp):
                saves.save(self.progress)

    def content(self) -> dict[str, Any]:
        return {"worlds": [_world(world) for world in WORLDS],
                "state": self.state(), "workshop": str(WORKSHOP),
                "project_root": str(self.project_root)}

    # fights
    def answer(self, body: dict[str, Any]) -> dict[str, Any]:
        riddles = _riddles(str(body.get("fight")))
        try:
            riddle = riddles[int(body.get("index", -1))]
        except (ValueError, IndexError):
            raise BadRequest("unknown riddle")
        given = body.get("answer")
        if riddle.kind == "choice":
            correct = given == riddle.answer
        else:
            accepted = riddle.answer if isinstance(riddle.answer,
                                                   tuple) else ()
            correct = str(given).strip().lower() in \
                [word.lower() for word in accepted]
        result: dict[str, Any] = {"correct": correct,
                                  "explain": riddle.explain}
        if riddle.kind == "choice" and isinstance(riddle.answer, int):
            result["answer"] = riddle.answer
        else:
            result["answer"] = list(riddle.answer) if isinstance(
                riddle.answer, tuple) else riddle.answer
        if riddle.run:
            output = run_code(riddle.code)
            result["output"] = (output.stdout + short_error(output.stderr)
                                ).rstrip()
        if correct:
            with self.lock:
                self.progress.xp += 5
                saves.save(self.progress)
        return result

    def fight_won(self, body: dict[str, Any]) -> dict[str, Any]:
        fight = str(body.get("fight"))
        _riddles(fight)
        self._award("fights", fight, 25)
        return self.state()

    # forge
    def _trial_path(self, chapter_id: str) -> tuple[Chapter, Path]:
        if chapter_id not in CHAPTERS:
            raise BadRequest(f"unknown chapter {chapter_id!r}")
        chapter = CHAPTERS[chapter_id]
        return chapter, WORKSHOP / chapter.trial.filename

    def _write(self, path: Path, body: dict[str, Any]) -> None:
        code = body.get("code")
        if isinstance(code, str):
            path.write_text(code)

    def forge_open(self, chapter_id: str) -> dict[str, Any]:
        chapter, path = self._trial_path(chapter_id)
        if not path.exists():
            path.write_text(chapter.trial.skeleton)
        return {"path": str(path), "code": path.read_text()}

    def forge_save(self, chapter_id: str,
                   body: dict[str, Any]) -> dict[str, Any]:
        _, path = self._trial_path(chapter_id)
        self._write(path, body)
        return {"saved": str(path)}

    def forge_reset(self, chapter_id: str) -> dict[str, Any]:
        chapter, path = self._trial_path(chapter_id)
        path.write_text(chapter.trial.skeleton)
        return {"code": chapter.trial.skeleton}

    def forge_run(self, chapter_id: str,
                  body: dict[str, Any]) -> dict[str, Any]:
        _, path = self._trial_path(chapter_id)
        self._write(path, body)
        return run_file(path, str(body.get("args", "")),
                        str(body.get("stdin", "")), WORKSHOP).as_dict()

    def forge_test(self, chapter_id: str,
                   body: dict[str, Any]) -> dict[str, Any]:
        _, path = self._trial_path(chapter_id)
        self._write(path, body)
        try:
            done = subprocess.run(
                [sys.executable, str(HARNESS), chapter_id, str(path)],
                capture_output=True, text=True, timeout=60, cwd=WORKSHOP)
            report: dict[str, Any] = json.loads(done.stdout)
        except subprocess.TimeoutExpired:
            report = {"load_error": "The tests ran for more than a minute "
                      "(an infinite loop?)", "results": []}
        except json.JSONDecodeError:
            report = {"load_error": "The test harness crashed: "
                      + short_error(done.stderr), "results": []}
        results = report["results"]
        passed = not report["load_error"] and bool(results) and \
            all(result["ok"] for result in results)
        report["passed"] = passed
        report["lint"] = self._lint(path) if passed else []
        if passed:
            self._award("forged", chapter_id, 50)
        report["state"] = self.state()
        return report

    @staticmethod
    def _lint(path: Path) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        for tool in ("flake8", "mypy"):
            if shutil.which(tool) is None:
                found.append({"tool": tool, "ok": None,
                              "output": f"{tool} is not installed: pip "
                                        f"install {tool}"})
                continue
            done = subprocess.run([tool, path.name], capture_output=True,
                                  text=True, timeout=60, cwd=path.parent)
            found.append({"tool": tool, "ok": done.returncode == 0,
                          "output": done.stdout.strip()})
        return found

    # sandbox and project
    def sandbox(self, body: dict[str, Any]) -> dict[str, Any]:
        folder = WORKSHOP / "sandbox"
        folder.mkdir(exist_ok=True)
        for name, content in SAMPLE_FILES.items():
            if not (folder / name).exists():
                (folder / name).write_text(content)
        return run_code(str(body.get("code", "")),
                        str(body.get("args", "")),
                        str(body.get("stdin", "")), folder).as_dict()

    def check(self, body: dict[str, Any]) -> dict[str, Any]:
        try:
            world = find_world(str(body.get("world")))
        except KeyError:
            raise BadRequest("unknown world")
        text = str(body.get("path") or self.project_root)
        root = Path(text).expanduser().resolve()
        if not root.is_dir():
            raise BadRequest(f"{root} is not a folder")
        reports = [report.as_dict()
                   for report in check_project(root, world.exercises)]
        all_ok = all(report["ok"] for report in reports)
        if all_ok:
            self._award("projects", world.id, 200)
        return {"root": str(root), "reports": reports, "ok": all_ok,
                "state": self.state()}

    def reset(self) -> dict[str, Any]:
        with self.lock:
            self.progress = saves.reset()
        return self.state()


# ---------------------------------------------------------------- HTTP

def make_handler(game: Game, token: str, port: int) -> type:
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            pass  # keep the terminal quiet

        def _send(self, status: int, body: bytes, kind: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, data: Any, status: int = 200) -> None:
            self._send(status, json.dumps(data).encode(),
                       "application/json")

        def _host_ok(self) -> bool:
            return self.headers.get("Host", "") in allowed_hosts

        def do_GET(self) -> None:
            if not self._host_ok():
                self._send(HTTPStatus.FORBIDDEN, b"Forbidden", "text/plain")
                return
            name = self.path.split("?")[0].lstrip("/") or "index.html"
            path = (WEB / name).resolve()
            if WEB not in path.parents or not path.is_file():
                self._send(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")
                return
            body = path.read_bytes()
            if name == "index.html":
                body = body.replace(b"__TOKEN__", token.encode())
            self._send(200, body, TYPES.get(path.suffix, "text/plain"))

        def do_POST(self) -> None:
            if not self._host_ok() or \
                    self.headers.get("X-Matrix-Token") != token:
                self._json({"error": "forbidden"}, HTTPStatus.FORBIDDEN)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(body, dict):
                    raise BadRequest("expected a JSON object")
                self._json(self._route(self.path, body))
            except BadRequest as error:
                self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            except (json.JSONDecodeError, ValueError) as error:
                self._json({"error": f"bad request: {error}"},
                           HTTPStatus.BAD_REQUEST)
            except Exception as error:  # never let the server die
                self._json({"error": f"{type(error).__name__}: {error}"},
                           HTTPStatus.INTERNAL_SERVER_ERROR)

        def _route(self, path: str, body: dict[str, Any]) -> Any:
            parts = path.strip("/").split("/")
            if parts == ["api", "game"]:
                return game.content()
            if parts == ["api", "answer"]:
                return game.answer(body)
            if parts == ["api", "fight_won"]:
                return game.fight_won(body)
            if parts == ["api", "sandbox"]:
                return game.sandbox(body)
            if parts == ["api", "check"]:
                return game.check(body)
            if parts == ["api", "reset"]:
                return game.reset()
            if len(parts) == 4 and parts[:2] == ["api", "forge"]:
                chapter_id, action = parts[2], parts[3]
                if action == "open":
                    return game.forge_open(chapter_id)
                if action == "save":
                    return game.forge_save(chapter_id, body)
                if action == "reset":
                    return game.forge_reset(chapter_id)
                if action == "run":
                    return game.forge_run(chapter_id, body)
                if action == "test":
                    return game.forge_test(chapter_id, body)
            raise BadRequest(f"unknown route {path}")

    return Handler


def serve(port: int, project_root: Path) -> tuple[ThreadingHTTPServer, str]:
    """Start listening; returns the server and the URL to open."""
    game = Game(project_root)
    token = secrets.token_hex(16)
    for candidate in range(port, port + 20):
        try:
            server = ThreadingHTTPServer(
                ("127.0.0.1", candidate),
                make_handler(game, token, candidate))
        except OSError:
            continue
        return server, f"http://127.0.0.1:{candidate}/"
    raise OSError(f"no free port between {port} and {port + 19}")
