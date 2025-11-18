"""Level serialization using JSON format."""
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from assets import MAPS_DIR, list_asset_files
from core.level import Level
from entities.base import Entity
from entities.player import Player
from entities.enemies import Enemy, Monster, Node
from entities.items import Collectible, Gate, Key

MAPS_PATH = MAPS_DIR


def list_maps():
    """List all available level files (JSON format)."""
    maps_dir = MAPS_PATH
    maps_dir.mkdir(parents=True, exist_ok=True)
    return [(str(path), path.stem) for path in maps_dir.glob("*.json")]


def get_files_paths_from_folder(folder, *folders):
    files = list_asset_files(folder, *folders)
    return files or None


def _entity_to_dict(entity: Entity, all_entities: List[Entity]) -> Dict[str, Any]:
    """Convert an entity to a dictionary representation."""
    base_data = {
        "position": {"px": entity.px, "py": entity.py}
    }
    
    if isinstance(entity, Player):
        return {"type": "player", **base_data}
    
    elif isinstance(entity, Collectible):
        return {"type": "collectible", **base_data}
    
    elif isinstance(entity, Key):
        return {"type": "key", **base_data}
    
    elif isinstance(entity, Gate):
        return {"type": "gate", **base_data}
    
    elif isinstance(entity, Node):
        # Find connected nodes by their indices in all_entities
        connected_indices = []
        for connected_node in entity.nodes:
            try:
                node_idx = all_entities.index(connected_node)
                connected_indices.append(node_idx)
            except ValueError:
                # Node not found in all_entities, skip
                pass
        return {
            "type": "node",
            **base_data,
            "connected_node_indices": connected_indices
        }
    
    elif isinstance(entity, (Enemy, Monster)):
        patrol_point_index = None
        if entity.patrolPoint is not None and isinstance(entity.patrolPoint, Node):
            try:
                patrol_point_index = all_entities.index(entity.patrolPoint)
            except ValueError:
                # Patrol point node not in all_entities, skip
                pass
        return {
            "type": "enemy",
            **base_data,
            "patrol_point_node_index": patrol_point_index
        }
    
    else:
        # Unknown entity type - try to preserve basic info
        return {
            "type": entity.__class__.__name__.lower(),
            **base_data
        }


def load_level_object(level_path: Path | str):
    """Load a level from JSON format."""
    level_path = Path(level_path)
    
    # Ensure .json extension
    if not level_path.suffix:
        level_path = level_path.with_suffix(".json")
    
    if not level_path.exists():
        raise FileNotFoundError(f"Level file not found: {level_path}")
    
    with open(level_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract grid
    grid = data["grid"]
    grid_np = np.array(grid, dtype=np.int16)
    
    # Reconstruct entities
    grid_entities = []
    node_entities = []
    nodes_by_index = {}
    
    # First pass: create all nodes
    for idx, entity_data in enumerate(data["entities"]):
        if entity_data["type"] == "node":
            pos = entity_data["position"]
            node = Node((pos["px"], pos["py"]))
            nodes_by_index[idx] = node
            node_entities.append(node)
    
    # Second pass: create other entities and link nodes
    for idx, entity_data in enumerate(data["entities"]):
        pos = entity_data["position"]
        entity_pos = (pos["px"], pos["py"])
        
        if entity_data["type"] == "player":
            grid_entities.append(Player(entity_pos))
        elif entity_data["type"] == "collectible":
            grid_entities.append(Collectible(entity_pos))
        elif entity_data["type"] == "key":
            grid_entities.append(Key(entity_pos))
        elif entity_data["type"] == "gate":
            grid_entities.append(Gate(entity_pos))
        elif entity_data["type"] == "enemy":
            patrol_point = None
            if entity_data.get("patrol_point_node_index") is not None:
                patrol_idx = entity_data["patrol_point_node_index"]
                if patrol_idx in nodes_by_index:
                    patrol_point = nodes_by_index[patrol_idx]
            grid_entities.append(Monster(entity_pos, patrolPoint=patrol_point))
        elif entity_data["type"] == "node":
            # Link nodes
            node = nodes_by_index[idx]
            for connected_idx in entity_data.get("connected_node_indices", []):
                if connected_idx in nodes_by_index:
                    node.join_node(nodes_by_index[connected_idx])
    
    # Create level object (compatible with existing Level.load)
    class LevelObject:
        def __init__(self):
            self.grid = grid
            self.grid_np = grid_np
            self.grid_entities = grid_entities
            self.node_entities = node_entities
            self.level_width = len(grid[0]) if grid else 0
            self.level_height = len(grid) if grid else 0
    
    return LevelObject()


def save_level(level_name: str, level: Level) -> None:
    """Save a level to JSON format."""
    # Convert grid (Level always has grid_np)
    grid = level.grid_np.tolist()
    
    # Collect all entities (grid entities + node entities)
    grid_entities = level.grid_entities
    node_entities = level.node_entities
    all_entities = list(grid_entities) + list(node_entities)
    
    # Convert entities to dictionaries
    entities = []
    for entity in all_entities:
        entity_dict = _entity_to_dict(entity, all_entities)
        entities.append(entity_dict)
    
    # Create level data structure
    level_data = {
        "version": 1,
        "grid": grid,
        "entities": entities
    }
    
    # Write JSON file
    output_path = MAPS_PATH / f"{level_name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(level_data, f, indent=2, ensure_ascii=False)

