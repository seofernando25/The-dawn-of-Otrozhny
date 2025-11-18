import math
import random

import assets
import audio
import levelData
import mathHelpers
import pathFinding
from .base import Entity, EnemyStatus, SpriteAgent
from .player import Player
from renderer.raycast import generate_distance_table


class Enemy(SpriteAgent):
    enemy_status = EnemyStatus.Normal
    enemy_status_time_left = 0

    def __init__(self, start_pos, patrolPoint=None):
        super().__init__(start_pos, 90, 2, 6, "Droog")
        self.patrolPoint = patrolPoint
        self.target = self.patrolPoint
        self.pathFindingNodesTarget = self.target
        self.pathFindingNodes = None
        self.timeGuarded = 0
        self.pathFindingComplete = False
        self.originalFov = self.FOV
        self.originalFovDepth = self.FOVDepth
        self.lastPathFindingPoint = None
        self.cameraYawSens = 4

    def update(self, dt, events):
        generate_distance_table(self)
        super().update(dt, events)
        current_map = levelData.require_current_map()
        player = Player.require_instance()
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

        if player in [x[0] for x in self.entitiesInSight]:
            self.canSeePlayer = True
            Enemy.change_enemy_status(EnemyStatus.Alert)
        else:
            self.canSeePlayer = False

        if self.canSeePlayer or Enemy.enemy_status == EnemyStatus.Alert:
            self.change_target(player)

        if Enemy.enemy_status == EnemyStatus.Evasion:
            if self.pathFindingNodesTarget != player:
                self.change_target(player)
            if self.pathFindingComplete:
                path_nodes = self.pathFindingNodes or []
                while len(path_nodes) == 0:
                    random_pos = Entity(current_map.pick_random_point())
                    self.change_target(random_pos)
                    path_nodes = self.pathFindingNodes or []

        if Enemy.enemy_status == EnemyStatus.Caution:
            if self.pathFindingComplete:
                random_pos = Entity(current_map.pick_random_point())
                dx, dy = mathHelpers.slope(self.get_pos(), random_pos.get_pos())
                targetDistance = math.hypot(dx, dy)
                path_nodes = self.pathFindingNodes or []
                if len(path_nodes) == 0 or targetDistance < 1:
                    while len(path_nodes) == 0 and targetDistance < 1:
                        random_pos = Entity(current_map.pick_random_point())
                        dx, dy = mathHelpers.slope(
                            self.get_pos(), random_pos.get_pos())
                        targetDistance = math.hypot(dx, dy)
                        path_nodes = self.pathFindingNodes or []

                self.change_target(random_pos)

        if (Enemy.enemy_status in (EnemyStatus.Evasion, EnemyStatus.Alert,
                                   EnemyStatus.Caution)):
            self.FOV = self.originalFov * 1.5
            self.FOVDepth = self.originalFovDepth * 1.5
        else:
            self.FOV = self.originalFov
            self.FOVDepth = self.originalFovDepth

        if self.target is not None:
            dx, dy = mathHelpers.slope(self.get_pos(), self.target.get_pos())
            targetDistance = math.hypot(dx, dy)
            if self.pathFindingNodes is not None and len(
                    self.pathFindingNodes) > 0:
                nextStep = self.pathFindingNodes[0]

                nextPathNodeDistance = mathHelpers.distance_to(
                    self.get_pos(), nextStep)
                adjustedNextStep = (nextStep[0] + 0.5, nextStep[1] + 0.5)
                self.move_to(Entity(adjustedNextStep), dt)
                if nextPathNodeDistance < 0.1:
                    self.pathFindingNodes.pop(0)
            else:
                self.pathFindingComplete = True
                if targetDistance > 0.5:
                    self.move_to(self.target, dt)

            if isinstance(self.target, Node) and targetDistance < 0.5:
                self.timeGuarded += dt
                self.rotate(math.radians(36) * dt)

                if self.timeGuarded > 1:
                    self.change_patrol_point()

    def change_target(self, target):
        if target is not None:
            self.target = target
            x, y = target.get_pos()
            my_pos = (int(self.px), int(self.py))
            self.lastPathFindingPoint = target.get_pos()
            self.pathFindingComplete = False
            self.pathFindingNodesTarget = target
            self.pathFindingNodes = pathFinding.go_to(my_pos, (int(x), int(y)))
            if self.pathFindingNodes and len(self.pathFindingNodes) > 0:
                self.pathFindingNodes.pop(0)

    def change_patrol_point(self):
        if self.target is None:
            return
        self.patrolPoint = self.target.pick_random_node()
        self.timeGuarded = 0
        self.change_target(self.patrolPoint)

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
            for _ in range(int(len(self.nodes) * 0.5)):
                node_list.append(node_list[-1])

        if len(node_list) > 0:
            node_pos = random.randint(0, len(node_list) - 1)
            return node_list[node_pos]
        else:
            return self


class Monster(Enemy):
    def __init__(self, start_pos, patrolPoint=None):
        super().__init__(start_pos, patrolPoint=patrolPoint)
        self.sound = None
        self.channel = None

    def update(self, dt, events):
        super().update(dt, events)
        self.channel = audio.ensure_channel(self.channel)

        dist_to_player = math.inf
        if self.target is not None:
            player = Player.require_instance()
            dist_to_player = mathHelpers.distance_to(
                self.get_pos(), player.get_pos())
            if isinstance(self.target, Player) and dist_to_player < 3 and self.canSeePlayer:
                self.attack(self.target, dt)
            if isinstance(self.target, Player) and dist_to_player < 3 and not self.canSeePlayer:
                self.look_at(self.target, dt)
        if dist_to_player < 5:
            self.play_sound(dist_to_player, Enemy.enemy_status.name)

    def play_sound(self, distance, flag, force=False):
        volume = mathHelpers.translate(distance, 0, 5, 2, 0.5)
        self.sound = assets.get_audio(self.agent_pack_name, flag)
        levels = (volume, volume)
        self.channel = audio.play_sound(
            self.sound,
            channel=self.channel,
            volume=levels,
            force=force)

    def attack(self, target, dt):
        if target is None:
            return
        self.look_at(target, dt * 2)
        target.health -= dt * 30
        target.look_at(self, dt)
        target.angleY += dt * random.randint(-400, 400)
        target.rotate(dt * random.randint(-3, 3))
        player = Player.require_instance()
        dist_to_player = mathHelpers.distance_to(self.get_pos(), player.get_pos())
        self.play_sound(dist_to_player, "Attack", True)

