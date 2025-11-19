import math
from typing import Optional, cast

import pygame

from config import ENTITY_DEFAULTS
from core import assets
from core.context import GameContext
from physics import movement
from utils import math_helpers
from utils.math_helpers import HasPosition


class Entity:
    """
    Base entity class for all game entities.

    Context is optional during entity creation (e.g., in level editor) but is
    required for gameplay operations. Context is automatically attached when
    a level is loaded via Level.attach_context().

    For gameplay, always ensure context is set before calling methods that
    require it (e.g., _player(), _current_map()).
    """

    def __init__(
        self,
        start_pos: tuple[float, float],
        *,
        context: Optional[GameContext] = None,
    ):
        self.px: float = float(start_pos[0])
        self.py: float = float(start_pos[1])
        self.context: Optional["GameContext"] = context

    def update(self, dt: float) -> None:
        pass

    def get_pos(self) -> tuple[float, float]:
        return (self.px, self.py)

    def set_context(self, context: GameContext) -> None:
        """Set the game context for this entity."""
        self.context = context

    def requires_context(self) -> GameContext:
        """
        Check if context is available and return it.

        Raises RuntimeError if context is not set. Context is typically
        set automatically when a level is loaded via Level.attach_context().
        """
        if self.context is None:
            raise RuntimeError(
                f"{self.__class__.__name__} requires a GameContext for this operation. "
                f"Set context via set_context() or pass context= to __init__(). "
                f"Context is typically set automatically when a level is loaded via Level.attach_context()."
            )
        return self.context

    def _current_map(self):
        """Get the current level/map from context."""
        context = self.requires_context()
        if not hasattr(context, "level") or context.level is None:
            raise RuntimeError(
                "GameContext.level is not set. "
                "This usually means the level hasn't been loaded yet. "
                "Ensure Level.load() has been called with a valid context."
            )
        return context.level

    def _player(self):
        """Get the player entity from context."""
        context = self.requires_context()
        if not hasattr(context, "player") or context.player is None:
            raise RuntimeError(
                "GameContext.player is not set. "
                "This usually means the player hasn't been initialized yet. "
                "Ensure a Player entity exists in the level and context has been updated."
            )
        return context.player


class SpriteEntity(Entity):
    def __init__(
        self,
        start_pos: tuple[float, float],
        agent_pack_name: str = "Default",
        *,
        context: Optional[GameContext] = None,
    ):
        super().__init__(start_pos, context=context)
        self.agent_pack_name = agent_pack_name

    def get_sprite(self, _cam: object):
        return assets.get_sprite(self.agent_pack_name, 0)


class Agent(SpriteEntity):
    def __init__(
        self,
        start_pos: tuple[float, float],
        fov: float,
        move_speed: float,
        fov_depth: float,
        *,
        context: Optional[GameContext] = None,
    ):
        super().__init__(start_pos, context=context)
        self.health = ENTITY_DEFAULTS["health"]
        self.entitiesInSight: list[tuple[HasPosition, float]] = []
        self.canSeePlayer = False
        self.rayDistanceTable: list[tuple[float, float, float, int, object] | None] = []
        self.fov = math.radians(fov)
        self.fov_depth = float(fov_depth)
        self.angleY = 0.0
        self.moveSpeed = float(move_speed)
        self.dirX = -1.0
        self.dirY = 0.0
        self.planeX = 0.0
        self.planeY = ENTITY_DEFAULTS["plane_y"]
        self.cameraYawSens = 0.0
        self.cameraPitchSens = 0.0

    def update(self, dt: float) -> None:
        return super().update(dt)

    def move(self, dirX: float, dirY: float, deltaTime: float) -> None:
        next_pos_x = self.px + dirX
        next_pos_y = self.py + dirY
        current_map = self._current_map()

        if 0 <= next_pos_x < current_map.level_width:
            if current_map.grid[int(next_pos_x)][int(self.py)] == 0:
                self.px = next_pos_x

        if 0 <= next_pos_y < current_map.level_height:
            if current_map.grid[int(self.px)][int(next_pos_y)] == 0:
                self.py = next_pos_y

    def move_to(self, target: HasPosition, deltaTime: float) -> None:
        """Move the agent towards a target using shared movement helpers."""
        look_mult = ENTITY_DEFAULTS["move_to_look_speed_multiplier"]
        movement.look_at(self, target, deltaTime * look_mult)
        dirX, dirY = movement.move_to_target(self, target, deltaTime)
        if dirX or dirY:
            self.move(dirX, dirY, deltaTime)

    def rotate(self, amount: float) -> None:
        oldDirX = self.dirX
        self.dirX = self.dirX * math.cos(amount) - self.dirY * math.sin(amount)
        self.dirY = oldDirX * math.sin(amount) + self.dirY * math.cos(amount)

        oldPlaneX = self.planeX
        self.planeX = self.planeX * math.cos(amount) - self.planeY * math.sin(amount)
        self.planeY = oldPlaneX * math.sin(amount) + self.planeY * math.cos(amount)

    def look_at(self, target: HasPosition, deltaTime: float) -> None:
        dx, dy = math_helpers.slope(self.get_pos(), target.get_pos())
        theta = math.atan2(dy, dx)
        angle = math.atan2(self.dirY, self.dirX)
        targetAngle = math.degrees(theta)
        shortest_angle = (
            (((targetAngle - math.degrees(angle)) % 360) + 540) % 360
        ) - 180
        self.rotate(math.radians(shortest_angle) * deltaTime)


class SpriteAgent(Agent):
    def __init__(
        self,
        start_pos: tuple[float, float],
        fov: float,
        move_speed: float,
        fov_depth: float,
        agent_pack: str,
        *,
        context: Optional["GameContext"] = None,
    ):
        super().__init__(start_pos, fov, move_speed, fov_depth, context=context)
        self.agent_pack_name = agent_pack

    def get_sprite(self, camObj: object) -> pygame.Surface:
        angle = math.atan2(self.dirY, self.dirX)
        if not hasattr(camObj, "get_pos"):
            return pygame.Surface((0, 0), pygame.SRCALPHA)
        camera_provider = cast(HasPosition, camObj)
        cam_pos = camera_provider.get_pos()
        camPos = (float(cam_pos[0]), float(cam_pos[1]))
        dx, dy = math_helpers.slope(camPos, self.get_pos())
        camAngleToSprite = math.atan2(dy, dx)
        angleCamDelta = math_helpers.fixed_angle(camAngleToSprite + angle)

        curr = assets.get_sprite(self.agent_pack_name, 0)
        if curr is None:
            return pygame.Surface((0, 0), pygame.SRCALPHA)
        if math.degrees(angleCamDelta) < 180:
            curr = pygame.transform.flip(curr, True, False)
        return curr
