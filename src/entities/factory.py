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
    """
    Factory for creating entities with optional context.
    
    Context is optional during entity creation (e.g., in level editor) but
    should be provided when creating entities for gameplay. Context will be
    automatically attached when a level is loaded via Level.attach_context().
    """
    
    @staticmethod
    def create(
        entity_type: str,
        position: Tuple[float, float],
        *,
        context: Optional["GameContext"] = None,
        **kwargs
    ) -> Entity:
        """
        Create an entity of the specified type.
        
        Args:
            entity_type: Type of entity to create (player, enemy, monster, node, etc.)
            position: Starting position as (x, y) tuple
            context: Optional game context. If provided, will be set on the entity.
            **kwargs: Additional arguments for entity-specific initialization
            
        Returns:
            Created entity instance
        """
        entity_class = ENTITY_REGISTRY.get(entity_type.lower())
        if entity_class is None:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        if entity_type.lower() in ("enemy", "monster"):
            patrol_point = kwargs.get("patrolPoint", kwargs.get("patrol_point"))
            entity = Monster(position, patrolPoint=patrol_point, context=context)
        elif entity_type.lower() == "node":
            entity = Node(position, context=context)
        elif entity_type.lower() == "player":
            entity = Player(position, context=context)
        else:
            # Other entities (Collectible, Key, Gate) also accept context
            entity = entity_class(position, context=context)
        
        # Ensure context is set if provided (some entities may not accept it in __init__)
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

