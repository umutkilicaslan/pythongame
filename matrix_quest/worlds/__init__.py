"""All the worlds of the game, in the order of the projects."""

from ..model import Chapter, Trial, World
from . import agents, construct, keymaker, oracle

WORLDS: list[World] = [construct.WORLD, agents.WORLD, oracle.WORLD,
                       keymaker.WORLD]

CHAPTERS: dict[str, Chapter] = {chapter.id: chapter for world in WORLDS
                                for chapter in world.chapters}

SAMPLE_FILES = {"keys.txt": keymaker.KEYS,
                "ancient_fragment.txt": keymaker.FRAGMENT}


def find_world(world_id: str) -> World:
    for world in WORLDS:
        if world.id == world_id:
            return world
    raise KeyError(f"no world {world_id!r}")


def find_trial(trial_id: str) -> Trial:
    try:
        return CHAPTERS[trial_id].trial
    except KeyError:
        raise KeyError(f"no trial {trial_id!r}")
