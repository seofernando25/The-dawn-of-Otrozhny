import math
from config import ENEMY_CONFIG
from physics import pathfinding
from renderer.raycast import generate_distance_table
from utils import math_helpers
from .base import Entity, EnemyStatus, SpriteAgent


class Enemy(SpriteAgent):
    """Base enemy class with AI behavior and pathfinding."""

    def __init__(self, start_pos, patrolPoint=None, *, context=None):
        super().__init__(
            start_pos,
            ENEMY_CONFIG["fov_degrees"],
            ENEMY_CONFIG["move_speed"],
            ENEMY_CONFIG["fov_depth"],
            ENEMY_CONFIG["sprite_pack"],
            context=context,
        )
        self.patrolPoint = patrolPoint
        self.target = self.patrolPoint
        self.pathFindingNodesTarget = self.target
        self.pathFindingNodes = None
        self.timeGuarded = 0
        self.pathFindingComplete = False
        self.originalFov = self.FOV
        self.originalFovDepth = self.FOVDepth
        self.lastPathFindingPoint = None
        self.cameraYawSens = ENEMY_CONFIG["camera_yaw_sensitivity"]

    def _enemy_state(self):
        """Get the shared enemy state manager from context."""
        context = self.requires_context()
        if not hasattr(context, "enemy_state") or context.enemy_state is None:
            raise RuntimeError(
                "GameContext.enemy_state is not set. "
                "This should be initialized automatically when creating a GameContext. "
                "Ensure build_game_context() is used to create the context."
            )
        return context.enemy_state

    def update(self, dt):
        """Update enemy AI behavior."""
        generate_distance_table(self)
        super().update(dt)
        current_map = self._current_map()
        player = self._player()
        # Timer logic is now handled by EnemyStateManager.update() in game loop
        
        enemy_state = self._enemy_state()
        if enemy_state.status == EnemyStatus.Normal:
            self.change_target(self.patrolPoint)

        player_entry = next(
            (entry for entry in self.entitiesInSight if entry[0] is player), None
        )
        self.canSeePlayer = player_entry is not None
        if self.canSeePlayer:
            enemy_state.change_status(EnemyStatus.Alert)

        if self.canSeePlayer or enemy_state.status == EnemyStatus.Alert:
            self.change_target(player)

        if enemy_state.status == EnemyStatus.Evasion:
            if self.pathFindingNodesTarget != player:
                self.change_target(player)
            if self.pathFindingComplete and not self.pathFindingNodes:
                self._retarget_random_point(current_map)

        if enemy_state.status == EnemyStatus.Caution:
            if self.pathFindingComplete and (
                not self.pathFindingNodes
                or self.target is None
                or math_helpers.distance_to(self.get_pos(), self.target.get_pos()) < 1
            ):
                self._retarget_random_point(current_map, min_distance=1.0)

        if enemy_state.status in (
            EnemyStatus.Evasion,
            EnemyStatus.Alert,
            EnemyStatus.Caution,
        ):
            self.FOV = self.originalFov * ENEMY_CONFIG["alert_fov_multiplier"]
            self.FOVDepth = self.originalFovDepth * ENEMY_CONFIG["alert_fov_depth_multiplier"]
        else:
            self.FOV = self.originalFov
            self.FOVDepth = self.originalFovDepth

        if self.target is not None:
            dx, dy = math_helpers.slope(self.get_pos(), self.target.get_pos())
            targetDistance = math.hypot(dx, dy)
            if self.pathFindingNodes is not None and len(self.pathFindingNodes) > 0:
                nextStep = self.pathFindingNodes[0]

                nextPathNodeDistance = math_helpers.distance_to(self.get_pos(), nextStep)
                adjustment = ENEMY_CONFIG["pathfinding_node_adjustment"]
                adjustedNextStep = (nextStep[0] + adjustment, nextStep[1] + adjustment)
                self.move_to(Entity(adjustedNextStep), dt)
                if nextPathNodeDistance < 0.1:
                    self.pathFindingNodes.pop(0)
            else:
                self.pathFindingComplete = True
                pathfinding_dist = ENEMY_CONFIG["pathfinding_target_distance"]
                if isinstance(pathfinding_dist, (int, float)) and targetDistance > pathfinding_dist:
                    self.move_to(self.target, dt)

            pathfinding_dist = ENEMY_CONFIG["pathfinding_target_distance"]
            from .node import Node
            if isinstance(self.target, Node) and isinstance(pathfinding_dist, (int, float)) and targetDistance < pathfinding_dist:
                self.timeGuarded += dt
                patrol_rot = ENEMY_CONFIG["patrol_rotation_speed"]
                if isinstance(patrol_rot, (int, float)):
                    rotation_speed = math.radians(patrol_rot) * dt
                else:
                    rotation_speed = 0
                self.rotate(rotation_speed)

                guard_time = ENEMY_CONFIG["patrol_guard_time"]
                if isinstance(guard_time, (int, float)) and self.timeGuarded > guard_time:
                    self.change_patrol_point()

    def change_target(self, target):
        """Change the enemy's target and recalculate pathfinding."""
        if target is not None:
            self.target = target
            x, y = target.get_pos()
            my_pos = (int(self.px), int(self.py))
            self.lastPathFindingPoint = target.get_pos()
            self.pathFindingComplete = False
            self.pathFindingNodesTarget = target
            current_map = self._current_map()
            self.pathFindingNodes = pathfinding.go_to(my_pos, (int(x), int(y)), current_map.grid)
            if self.pathFindingNodes and len(self.pathFindingNodes) > 0:
                self.pathFindingNodes.pop(0)

    def change_patrol_point(self):
        """Change to a new random patrol point."""
        if self.target is None:
            return
        self.patrolPoint = self.target.pick_random_node()
        self.timeGuarded = 0
        self.change_target(self.patrolPoint)

    def _retarget_random_point(self, current_map, min_distance=0.0, attempts=None):
        """Retarget to a random point on the map."""
        if attempts is None:
            retarget_attempts = ENEMY_CONFIG["retarget_attempts"]
            attempts = int(retarget_attempts) if isinstance(retarget_attempts, (int, float)) else 10
        for _ in range(attempts):
            random_entity = Entity(current_map.pick_random_point())
            distance = math_helpers.distance_to(self.get_pos(), random_entity.get_pos())
            if distance < min_distance:
                continue
            self.change_target(random_entity)
            if self.pathFindingNodes:
                return True
        return False

    def change_enemy_status(self, status):
        """Change the shared enemy status. Requires context to be set."""
        self._enemy_state().change_status(status)

