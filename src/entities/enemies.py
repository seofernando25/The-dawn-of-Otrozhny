import math
import random

import audio_manager
from utils import math_helpers
from physics import pathfinding
from config import ENEMY_CONFIG, DAMAGE_CONFIG, SOUND_CONFIG
from .base import Entity, EnemyStatus, SpriteAgent
from renderer.raycast import generate_distance_table


class Enemy(SpriteAgent):
    enemy_status = EnemyStatus.Normal
    enemy_status_time_left = 0

    def __init__(self, start_pos, patrolPoint=None):
        super().__init__(
            start_pos,
            ENEMY_CONFIG["fov_degrees"],
            ENEMY_CONFIG["move_speed"],
            ENEMY_CONFIG["fov_depth"],
            ENEMY_CONFIG["sprite_pack"],
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

    def update(self, dt, events):
        generate_distance_table(self)
        super().update(dt, events)
        current_map = self._current_map()
        player = self._player()
        Enemy.enemy_status_time_left -= dt
        if Enemy.enemy_status_time_left < 0:
            Enemy.enemy_status_time_left = 0
            if Enemy.enemy_status == EnemyStatus.Alert:
                Enemy.enemy_status = EnemyStatus.Evasion
            elif Enemy.enemy_status == EnemyStatus.Evasion:
                Enemy.enemy_status = EnemyStatus.Caution
            elif Enemy.enemy_status == EnemyStatus.Caution:
                Enemy.enemy_status = EnemyStatus.Normal

            if Enemy.enemy_status != EnemyStatus.Normal:
                Enemy.reset_enemy_status_time()

        if Enemy.enemy_status == EnemyStatus.Normal:
            self.change_target(self.patrolPoint)

        player_entry = next(
            (entry for entry in self.entitiesInSight if entry[0] is player), None
        )
        self.canSeePlayer = player_entry is not None
        if self.canSeePlayer:
            Enemy.change_enemy_status(EnemyStatus.Alert)

        if self.canSeePlayer or Enemy.enemy_status == EnemyStatus.Alert:
            self.change_target(player)

        if Enemy.enemy_status == EnemyStatus.Evasion:
            if self.pathFindingNodesTarget != player:
                self.change_target(player)
            if self.pathFindingComplete and not self.pathFindingNodes:
                self._retarget_random_point(current_map)

        if Enemy.enemy_status == EnemyStatus.Caution:
            if self.pathFindingComplete and (
                not self.pathFindingNodes
                or self.target is None
                or math_helpers.distance_to(self.get_pos(), self.target.get_pos()) < 1
            ):
                self._retarget_random_point(current_map, min_distance=1.0)

        if Enemy.enemy_status in (
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
        if self.target is None:
            return
        self.patrolPoint = self.target.pick_random_node()
        self.timeGuarded = 0
        self.change_target(self.patrolPoint)

    def _retarget_random_point(self, current_map, min_distance=0.0, attempts=None):
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

    @staticmethod
    def change_enemy_status(status):
        Enemy.enemy_status = status
        Enemy.enemy_status_time_left = Enemy.enemy_status.value[2]

    @staticmethod
    def reset_enemy_status_time():
        Enemy.enemy_status_time_left = Enemy.enemy_status.value[2]


class Node(Entity):
    def __init__(self, start_pos):
        super().__init__(start_pos)
        self.behaviour = None
        self.destination_point = 0
        self.nodes = []

    def join_node(self, nextNode):
        if nextNode not in self.nodes:
            self.nodes.append(nextNode)
        if self not in nextNode.nodes:
            nextNode.nodes.append(self)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            node.remove_node(self)

    def pick_random_node(self, biased=False):
        node_list = self.nodes.copy()

        if biased:
            from config import ENEMY_CONFIG
            bias_factor = ENEMY_CONFIG["node_bias_factor"]
            for _ in range(int(len(self.nodes) * bias_factor)):
                node_list.append(node_list[-1])

        if len(node_list) > 0:
            node_pos = random.randint(0, len(node_list) - 1)
            return node_list[node_pos]
        else:
            return self


class Monster(Enemy):
    def __init__(self, start_pos, patrolPoint=None):
        super().__init__(start_pos, patrolPoint=patrolPoint)

    def update(self, dt, events):
        super().update(dt, events)

        dist_to_player = math.inf
        if self.target is not None:
            player = self._player()
            dist_to_player = math_helpers.distance_to(self.get_pos(), player.get_pos())
            attack_dist = ENEMY_CONFIG["attack_distance"]
            if isinstance(attack_dist, (int, float)):
                if self.target is player and dist_to_player < attack_dist and self.canSeePlayer:
                    self.attack(player, dt)
                if self.target is player and dist_to_player < attack_dist and not self.canSeePlayer:
                    self.look_at(player, dt)
        sound_dist = ENEMY_CONFIG["sound_trigger_distance"]
        if isinstance(sound_dist, (int, float)) and dist_to_player < sound_dist:
            self.play_sound(dist_to_player, Enemy.enemy_status.name)

    def play_sound(self, distance, flag, force=False):
        volume = math_helpers.translate(
            distance,
            SOUND_CONFIG["volume_distance_min"],
            SOUND_CONFIG["volume_distance_max"],
            SOUND_CONFIG["volume_max"],
            SOUND_CONFIG["volume_min"],
        )
        levels = (volume, volume)
        audio_manager.play_sound(
            flag,
            pack=self.agent_pack_name,
            volume=levels,
            force=force,
        )

    def attack(self, target, dt):
        if target is None:
            return
        look_mult = ENEMY_CONFIG["attack_look_speed_multiplier"]
        self.look_at(target, dt * look_mult)
        target.health -= dt * DAMAGE_CONFIG["enemy_attack_dps"]
        target.look_at(self, dt)
        angle_range = ENEMY_CONFIG["attack_angle_range"]
        if isinstance(angle_range, tuple) and len(angle_range) == 2:
            angle_min, angle_max = angle_range
            target.angleY += dt * random.randint(int(angle_min), int(angle_max))
        rot_range = ENEMY_CONFIG["attack_rotation_range"]
        if isinstance(rot_range, tuple) and len(rot_range) == 2:
            rot_min, rot_max = rot_range
            target.rotate(dt * random.randint(int(rot_min), int(rot_max)))
        player = self._player()
        dist_to_player = math_helpers.distance_to(self.get_pos(), player.get_pos())
        self.play_sound(dist_to_player, "Attack", True)
