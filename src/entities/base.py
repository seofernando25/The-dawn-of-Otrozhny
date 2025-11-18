import enum
import math
from typing import Optional, TYPE_CHECKING

import pygame

import assets
import colors
from utils import math_helpers
from config import ENTITY_DEFAULTS
from physics import movement

if TYPE_CHECKING:
    from core.context import GameContext


class Entity:
    def __init__(self, start_pos, *, context: Optional["GameContext"] = None):
        self.px = start_pos[0]
        self.py = start_pos[1]
        self.context: Optional["GameContext"] = context

    def update(self, dt, events):
        pass

    def get_pos(self):
        return (self.px, self.py)

    def set_context(self, context: "GameContext") -> None:
        """Set the game context for this entity.
        
        Args:
            context: The game context containing level, player, and other game state.
        """
        self.context = context

    def requires_context(self) -> "GameContext":
        """Check if context is available and return it.
        
        This helper method provides clear error messages when context-dependent
        operations are attempted without a context being set.
        
        Returns:
            The GameContext instance.
            
        Raises:
            RuntimeError: If context is not set, with a helpful error message
                explaining how to fix it.
        """
        if self.context is None:
            raise RuntimeError(
                f"{self.__class__.__name__} requires a GameContext for this operation. "
                f"Set context via set_context() or pass context= to __init__(). "
                f"Context is typically set automatically when a level is loaded."
            )
        return self.context

    def _current_map(self):
        """Get the current level/map from context.
        
        Returns:
            The Level instance from the game context.
            
        Raises:
            RuntimeError: If context is not set or level is not available.
        """
        context = self.requires_context()
        if not hasattr(context, "level") or context.level is None:
            raise RuntimeError(
                f"GameContext.level is not set. "
                f"This usually means the level hasn't been loaded yet. "
                f"Ensure Level.load() has been called with a valid context."
            )
        return context.level

    def _player(self):
        """Get the player entity from context.
        
        Returns:
            The Player instance from the game context.
            
        Raises:
            RuntimeError: If context is not set or player is not available.
        """
        context = self.requires_context()
        if not hasattr(context, "player") or context.player is None:
            raise RuntimeError(
                f"GameContext.player is not set. "
                f"This usually means the player hasn't been initialized yet. "
                f"Ensure a Player entity exists in the level and context has been updated."
            )
        return context.player


class SpriteEntity(Entity):
    def __init__(
        self, start_pos, agent_pack_name="Default", *, context: Optional["GameContext"] = None
    ):
        super().__init__(start_pos, context=context)
        self.agent_pack_name = agent_pack_name

    def get_sprite(self, _cam):
        return assets.get_sprite(self.agent_pack_name, 0)


class Agent(SpriteEntity):
    def __init__(
        self,
        start_pos,
        fov,
        move_speed,
        fov_depth,
        *,
        context: Optional["GameContext"] = None,
    ):
        super().__init__(start_pos, context=context)
        self.health = ENTITY_DEFAULTS["health"]
        self.entitiesInSight = []
        self.canSeePlayer = False
        self.rayDistanceTable = {}
        self.FOV = fov * (math.pi / 180)
        self.FOVDepth = fov_depth
        self.angleY = 0
        self.moveSpeed = move_speed
        self.dirX = -1
        self.dirY = 0
        self.planeX = 0
        self.planeY = ENTITY_DEFAULTS["plane_y"]
        self.cameraYawSens = 0
        self.cameraPitchSens = 0

    def update(self, dt, events):
        return super().update(dt, events)

    def move(self, dirX, dirY, deltaTime):
        next_pos_x = self.px + dirX
        next_pos_y = self.py + dirY
        current_map = self._current_map()

        if next_pos_x < 0 or next_pos_x > current_map.level_width:
            self.px += dirX
        elif self.py < 0 or self.py > current_map.level_height:
            self.px += dirX
        elif current_map.grid[int(next_pos_x)][int(self.py)] == 0:
            self.px += dirX

        if next_pos_y < 0 or next_pos_y > current_map.level_height:
            self.py += dirY
        elif self.px < 0 or self.px > current_map.level_width:
            self.py += dirY
        elif current_map.grid[int(self.px)][int(next_pos_y)] == 0:
            self.py += dirY

    def move_to(self, target, deltaTime):
        """Move the agent towards a target using shared movement helpers."""
        look_mult = ENTITY_DEFAULTS["move_to_look_speed_multiplier"]
        movement.look_at(self, target, deltaTime * look_mult)
        dirX, dirY = movement.move_to_target(self, target, deltaTime)
        if dirX or dirY:
            self.move(dirX, dirY, deltaTime)

    def rotate(self, amount):
        oldDirX = self.dirX
        self.dirX = self.dirX * math.cos(amount) - self.dirY * math.sin(amount)
        self.dirY = oldDirX * math.sin(amount) + self.dirY * math.cos(amount)

        oldPlaneX = self.planeX
        self.planeX = self.planeX * math.cos(amount) - self.planeY * math.sin(amount)
        self.planeY = oldPlaneX * math.sin(amount) + self.planeY * math.cos(amount)

    def look_at(self, target, deltaTime):
        dx, dy = math_helpers.slope(self.get_pos(), target.get_pos())
        theta = math.atan2(dy, dx)
        angle = math.atan2(self.dirY, self.dirX)
        targetAngle = math.degrees(theta)
        shortest_angle = (
            (((targetAngle - math.degrees(angle)) % 360) + 540) % 360
        ) - 180
        self.rotate(math.radians(shortest_angle) * deltaTime)


class EnemyStatus(enum.Enum):
    Normal = ("Normal", colors.GREEN, 0)
    Alert = ("Alert", colors.RED, 10)
    Evasion = ("Evasion", colors.YELLOW, 20)
    Caution = ("Caution", colors.MAROON, 30)


class SpriteAgent(Agent):
    def __init__(
        self,
        start_pos,
        fov,
        move_speed,
        fov_depth,
        agent_pack,
        *,
        context: Optional["GameContext"] = None,
    ):
        super().__init__(start_pos, fov, move_speed, fov_depth, context=context)
        self.agent_pack_name = agent_pack

    def get_sprite(self, camObj):
        angle = math.atan2(self.dirY, self.dirX)
        camPos = camObj.get_pos()
        dx, dy = math_helpers.slope(camPos, self.get_pos())
        camAngleToSprite = math.atan2(dy, dx)
        angleCamDelta = math_helpers.fixed_angle(camAngleToSprite + angle)

        curr = assets.get_sprite(self.agent_pack_name, 0)
        if math.degrees(angleCamDelta) < 180:
            curr = pygame.transform.flip(curr, True, False)
        return curr
