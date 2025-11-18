"""Level serialization using JSON format with Pydantic validation."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

import numpy as np

from core.assets import MAPS_DIR, list_asset_files
from core.level import Level
from core.level_format import (
    LevelData,
    PlayerData,
    CollectibleData,
    KeyData,
    GateData,
    NodeData,
    EnemyData,
    Position,
)
from entities.base import Entity
from entities.player import Player
from entities.enemy import Enemy
from entities.monster import Monster
from entities.node import Node
from entities.items import Collectible, Gate, Key
from entities.factory import EntityFactory

MAPS_PATH = MAPS_DIR


@dataclass
class LevelObject:
    """Data container for level data loaded from JSON files.
    
    This is used as an intermediate representation before creating
    a full Level instance with context attached.
    """
    grid: List[List[int]]
    grid_np: np.ndarray
    grid_entities: List[Entity]
    node_entities: List[Node]
    
    @property
    def level_width(self) -> int:
        """Width of the level grid."""
        return len(self.grid[0]) if self.grid else 0
    
    @property
    def level_height(self) -> int:
        """Height of the level grid."""
        return len(self.grid) if self.grid else 0


def list_maps():
    """List all available level files (JSON format)."""
    maps_dir = MAPS_PATH
    maps_dir.mkdir(parents=True, exist_ok=True)
    return [(str(path), path.stem) for path in maps_dir.glob("*.json")]


def get_files_paths_from_folder(folder, *folders):
    files = list_asset_files(folder, *folders)
    return files or None


def _entity_to_data(entity: Entity, all_entities: List[Entity]) -> Union[
    PlayerData, CollectibleData, KeyData, GateData, NodeData, EnemyData
]:
    """Convert an entity to a Pydantic model representation."""
    position = Position(px=entity.px, py=entity.py)
    
    if isinstance(entity, Player):
        return PlayerData(position=position)
    
    elif isinstance(entity, Collectible):
        return CollectibleData(position=position)
    
    elif isinstance(entity, Key):
        return KeyData(position=position)
    
    elif isinstance(entity, Gate):
        return GateData(position=position)
    
    elif isinstance(entity, Node):
        connected_indices = []
        for connected_node in entity.nodes:
            try:
                node_idx = all_entities.index(connected_node)
                connected_indices.append(node_idx)
            except ValueError:
                # Node not found in all_entities, skip
                pass
        return NodeData(
            position=position,
            connected_node_indices=connected_indices
        )
    
    elif isinstance(entity, (Enemy, Monster)):
        patrol_point_index = None
        if entity.patrolPoint is not None and isinstance(entity.patrolPoint, Node):
            try:
                patrol_point_index = all_entities.index(entity.patrolPoint)
            except ValueError:
                # Patrol point node not in all_entities, skip
                pass
        return EnemyData(
            position=position,
            patrol_point_node_index=patrol_point_index
        )
    
    else:
        # Unknown entity type - raise error instead of silently failing
        raise ValueError(
            f"Unknown entity type: {entity.__class__.__name__}. "
            f"Supported types: Player, Collectible, Key, Gate, Node, Enemy, Monster"
        )


def load_level_object(level_path: Path | str):
    """Load a level from JSON format with Pydantic validation."""
    level_path = Path(level_path)
    
    # Ensure .json extension
    if not level_path.suffix:
        level_path = level_path.with_suffix(".json")
    
    if not level_path.exists():
        raise FileNotFoundError(f"Level file not found: {level_path}")
    
    with open(level_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    # Parse and validate using Pydantic model
    try:
        level_data = LevelData.model_validate(json_data)
    except Exception as e:
        raise ValueError(
            f"Invalid level data in {level_path}: {e}. "
            f"Please check the level file format."
        ) from e
    
    # Extract grid
    grid = level_data.grid
    grid_np = np.array(grid, dtype=np.int16)
    
    # Reconstruct entities
    grid_entities = []
    node_entities = []
    nodes_by_index = {}
    
    # First pass: create all nodes
    for idx, entity_data in enumerate(level_data.entities):
        if isinstance(entity_data, NodeData):
            node = EntityFactory.create(
                "node",
                (entity_data.position.px, entity_data.position.py)
            )
            nodes_by_index[idx] = node
            node_entities.append(node)
    
    # Second pass: create other entities and link nodes
    for idx, entity_data in enumerate(level_data.entities):
        if isinstance(entity_data, NodeData):
            # Link nodes
            node = nodes_by_index[idx]
            for connected_idx in entity_data.connected_node_indices:
                if connected_idx in nodes_by_index:
                    node.join_node(nodes_by_index[connected_idx])
        else:
            entity_dict = entity_data.model_dump()
            entity = EntityFactory.create_from_data(
                entity_dict,
                nodes_by_index=nodes_by_index
            )
            
            if isinstance(entity, Node):
                node_entities.append(entity)
            else:
                grid_entities.append(entity)
    
    return LevelObject(
        grid=grid,
        grid_np=grid_np,
        grid_entities=grid_entities,
        node_entities=node_entities,
    )


def save_level(level_name: str, level: Level) -> None:
    """Save a level to JSON format using Pydantic models for validation."""
    # Convert grid (Level always has grid_np)
    grid = level.grid_np.tolist()
    
    # Collect all entities (grid entities + node entities)
    grid_entities = level.grid_entities
    node_entities = level.node_entities
    all_entities = list(grid_entities) + list(node_entities)
    
    # Convert entities to Pydantic models
    entity_data_list = []
    for entity in all_entities:
        entity_data = _entity_to_data(entity, all_entities)
        entity_data_list.append(entity_data)
    
    level_data = LevelData(
        version=1,
        grid=grid,
        entities=entity_data_list
    )
    
    output_path = MAPS_PATH / f"{level_name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json_str = level_data.model_dump_json(indent=2, exclude_none=False)
        f.write(json_str)

