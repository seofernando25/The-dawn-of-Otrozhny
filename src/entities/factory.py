"""Entity factory for creating entities with proper context handling."""
from typing import Optional, Tuple, Dict, Type, TYPE_CHECKING
from entities.base import Entity
from entities.player import Player
from entities.monster import Monster
from entities.node import Node
from entities.items import Collectible, Key, Gate

if TYPE_CHECKING:
    from core.context import GameContext


ENTITY_REGISTRY: Dict[str, Type[Entity]] = {
    "player": Player,
    "enemy": Monster,
    "monster": Monster,
    "node": Node,
    "collectible": Collectible,
    "key": Key,
    "gate": Gate,
}


class EntityFactory:
    """Factory for creating entities with optional context."""
    
    @staticmethod
    def create(
        entity_type: str,
        position: Tuple[float, float],
        *,
        context: Optional["GameContext"] = None,
        **kwargs
    ) -> Entity:
        """Create an entity of the specified type."""
        entity_class = ENTITY_REGISTRY.get(entity_type.lower())
        if entity_class is None:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        if entity_type.lower() in ("enemy", "monster"):
            patrol_point = kwargs.get("patrolPoint", kwargs.get("patrol_point"))
            entity = Monster(position, patrolPoint=patrol_point)
        elif entity_type.lower() == "node":
            entity = Node(position)
        elif entity_type.lower() == "player":
            entity = Player(position, context=context)
        else:
            entity = entity_class(position)
        
        if context is not None and hasattr(entity, "set_context"):
            entity.set_context(context)
        
        return entity
    
    @staticmethod
    def create_from_data(
        entity_data: dict,
        *,
        context: Optional["GameContext"] = None,
        nodes_by_index: Optional[Dict[int, Node]] = None
    ) -> Entity:
        """Create an entity from serialized data."""
        entity_type = entity_data["type"]
        pos = entity_data["position"]
        position = (pos["px"], pos["py"])
        
        kwargs = {}
        if entity_type == "enemy":
            if nodes_by_index and "patrol_point_node_index" in entity_data:
                patrol_idx = entity_data.get("patrol_point_node_index")
                if patrol_idx is not None and patrol_idx in nodes_by_index:
                    kwargs["patrolPoint"] = nodes_by_index[patrol_idx]
        
        return EntityFactory.create(entity_type, position, context=context, **kwargs)
    
    @staticmethod
    def register(entity_type: str, entity_class: Type[Entity]) -> None:
        """Register a new entity type with the factory."""
        ENTITY_REGISTRY[entity_type.lower()] = entity_class

