# Used this for serialization
# and deserialization of files in the game
import pickle

import numpy as np

import levelData
from assets import MAPS_DIR, list_asset_files, list_maps as _list_maps

MAPS_PATH = MAPS_DIR


def list_maps():
    return _list_maps()


def get_files_paths_from_folder(folder, *folders):
    files = list_asset_files(folder, *folders)
    return files or None


def _ensure_entity_aliases():
    import entities as entities_pkg
    from entities.base import Agent, EnemyStatus, Entity, SpriteAgent, SpriteEntity
    from entities.enemies import Enemy, Monster, Node
    from entities.items import Collectible, Gate, Key
    from entities.player import Player, get_input

    alias_map = {
        "Agent": Agent,
        "EnemyStatus": EnemyStatus,
        "Entity": Entity,
        "SpriteAgent": SpriteAgent,
        "SpriteEntity": SpriteEntity,
        "Enemy": Enemy,
        "Monster": Monster,
        "Node": Node,
        "Collectible": Collectible,
        "Gate": Gate,
        "Key": Key,
        "Player": Player,
        "get_input": get_input,
    }
    for name, obj in alias_map.items():
        setattr(entities_pkg, name, obj)


def load_level(level_path):
    _ensure_entity_aliases()
    with open(level_path, "rb") as level:
        level_data = pickle.load(level)
        levelData.Level.load(level_data)


def load_level_object(level_path):
    _ensure_entity_aliases()
    with open(level_path, "rb") as level:
        level_data = pickle.load(level)
        if getattr(level_data, "grid_np", None) is None:
            try:
                level_data.grid_np = np.array(level_data.grid, dtype=np.int16)
            except Exception:
                pass
        return level_data


def save_level(level_name, level):
    with open(MAPS_PATH / f"{level_name}.map", "wb") as dest:
        pickle.dump(level, dest)

