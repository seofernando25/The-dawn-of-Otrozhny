from __future__ import annotations

from typing import Literal, List, Optional, Union
from pydantic import BaseModel, Field


class Position(BaseModel):
    """2D position."""
    px: float
    py: float


class EntityData(BaseModel):
    """Base entity data."""
    type: str
    position: Position


class PlayerData(BaseModel):
    """Player entity data."""
    type: Literal["player"] = "player"
    position: Position


class CollectibleData(BaseModel):
    """Collectible item data."""
    type: Literal["collectible"] = "collectible"
    position: Position


class KeyData(BaseModel):
    """Key item data."""
    type: Literal["key"] = "key"
    position: Position


class GateData(BaseModel):
    """Gate entity data."""
    type: Literal["gate"] = "gate"
    position: Position


class NodeData(BaseModel):
    """Pathfinding node data."""
    type: Literal["node"] = "node"
    position: Position
    # Node connections are stored by index in the level
    connected_node_indices: List[int] = Field(default_factory=list)


class EnemyData(BaseModel):
    """Enemy entity data."""
    type: Literal["enemy"] = "enemy"
    position: Position
    # Patrol point is stored as index of a node, or None
    patrol_point_node_index: Optional[int] = None


class LevelData(BaseModel):
    """Complete level data structure."""
    version: int = Field(default=1, description="Format version")
    grid: List[List[int]] = Field(description="2D grid where 0=empty, 1=wall")
    entities: List[
        Union[PlayerData, CollectibleData, KeyData, GateData, EnemyData, NodeData]
    ] = Field(
        description="All entities in the level",
        discriminator="type"
    )

