from __future__ import annotations

import logging
import random
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Sequence

import pygame

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "Assets"
MAPS_DIR = ROOT / "Maps"

_AUDIO_CACHE = {}


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_asset_files(*parts: Sequence[str]) -> List[str]:
    target = ASSETS_DIR.joinpath(*parts)
    if not target.exists():
        LOGGER.warning("Asset directory missing: %s", target)
        return []
    return sorted(str(p) for p in target.iterdir() if p.is_file())


def iter_asset_files(*parts: Sequence[str]) -> Iterable[Path]:
    target = ASSETS_DIR.joinpath(*parts)
    if not target.exists():
        LOGGER.warning("Asset directory missing: %s", target)
        return []
    return (p for p in sorted(target.iterdir()) if p.is_file())


@lru_cache(maxsize=256)
def get_sprite(sprite_pack: str, sprite_position: int):
    if not sprite_pack:
        return None
    filenames = list_asset_files(sprite_pack, "Sprites")
    if not filenames:
        if sprite_pack:
            LOGGER.warning("Sprite pack '%s' is missing sprites.", sprite_pack)
        return None
    try:
        sprite_path = filenames[sprite_position]
    except IndexError:
        sprite_path = filenames[0]
    image = pygame.image.load(sprite_path).convert_alpha()
    image.set_colorkey((152, 0, 136))
    return image


def get_audio(folder: str, state: str):
    cache_key = (folder, state)
    cached_sounds = _AUDIO_CACHE.get(cache_key)
    if cached_sounds:
        return random.choice(cached_sounds)

    filenames = list_asset_files(folder, state)
    if not filenames:
        LOGGER.warning("Audio folder '%s/%s' is missing.", folder, state)
        return None
    sounds = [pygame.mixer.Sound(path) for path in filenames]
    _AUDIO_CACHE[cache_key] = sounds
    return random.choice(sounds)


@lru_cache(maxsize=8)
def get_cached_audio(folder_name: str, sub_folder: str):
    filenames = list_asset_files(folder_name, sub_folder)
    if not filenames:
        LOGGER.warning("Cached audio folder '%s/%s' missing.", folder_name,
                       sub_folder)
        return None
    return pygame.mixer.Sound(filenames[0])


def list_maps():
    maps_dir = _ensure_dir(MAPS_DIR)
    return [(str(path), path.stem) for path in maps_dir.glob("*.map")]


def list_asset_packs():
    if not ASSETS_DIR.exists():
        LOGGER.warning("Assets directory missing: %s", ASSETS_DIR)
        return []
    packs = []
    for path in ASSETS_DIR.iterdir():
        if path.is_dir() and (path / "Sprites").exists():
            packs.append(path.name)
    return sorted(packs)

