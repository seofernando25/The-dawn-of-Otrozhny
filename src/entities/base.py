import enum
import math

import pygame

import assets
import colors
import mathHelpers
from physics import movement
class Entity:
    def __init__(self, start_pos):
        self.px = start_pos[0]
        self.py = start_pos[1]

    def update(self, dt, events):
        pass

    def get_pos(self):
        return (self.px, self.py)


class SpriteEntity(Entity):
    def __init__(self, start_pos, agent_pack_name="Default"):
        super().__init__(start_pos)
        self.agent_pack_name = agent_pack_name

    def get_sprite(self, _cam):
        return assets.get_sprite(self.agent_pack_name, 0)


class Agent(SpriteEntity):
    def __init__(self, start_pos, fov, move_speed, fov_depth):
        super().__init__(start_pos)
        self.health = 100
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
        self.planeY = 0.66
        self.cameraYawSens = 0
        self.cameraPitchSens = 0

    def update(self, dt, events):
        return super().update(dt, events)

    def move(self, dirX, dirY, deltaTime):
        import levelData
        next_pos_x = self.px + dirX
        next_pos_y = self.py + dirY
        current_map = levelData.require_current_map()

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
        movement.look_at(self, target, deltaTime * 2)
        dirX, dirY = movement.move_to_target(self, target, deltaTime)
        if dirX or dirY:
            self.move(dirX, dirY, deltaTime)

    def rotate(self, amount):
        oldDirX = self.dirX
        self.dirX = self.dirX * math.cos(amount) - self.dirY * math.sin(amount)
        self.dirY = oldDirX * math.sin(amount) + self.dirY * math.cos(amount)

        oldPlaneX = self.planeX
        self.planeX = (self.planeX * math.cos(amount) -
                       self.planeY * math.sin(amount))
        self.planeY = oldPlaneX * math.sin(amount) + self.planeY * math.cos(amount)

    def look_at(self, target, deltaTime):
        dx, dy = mathHelpers.slope(self.get_pos(), target.get_pos())
        theta = math.atan2(dy, dx)
        angle = math.atan2(self.dirY, self.dirX)
        targetAngle = math.degrees(theta)
        shortest_angle = ((((targetAngle - math.degrees(angle)) % 360) + 540) %
                          360) - 180
        self.rotate(math.radians(shortest_angle) * deltaTime)


class EnemyStatus(enum.Enum):
    Normal = ("Normal", colors.GREEN, 0)
    Alert = ("Alert", colors.RED, 10)
    Evasion = ("Evasion", colors.YELLOW, 20)
    Caution = ("Caution", colors.MAROON, 30)


class SpriteAgent(Agent):
    def __init__(self, start_pos, fov, move_speed, fov_depth, agent_pack):
        super().__init__(start_pos, fov, move_speed, fov_depth)
        self.agent_pack_name = agent_pack

    def get_sprite(self, camObj):
        angle = math.atan2(self.dirY, self.dirX)
        camPos = camObj.get_pos()
        dx, dy = mathHelpers.slope(camPos, self.get_pos())
        camAngleToSprite = math.atan2(dy, dx)
        angleCamDelta = mathHelpers.fixed_angle(camAngleToSprite + angle)

        curr = assets.get_sprite(self.agent_pack_name, 0)
        if math.degrees(angleCamDelta) < 180:
            curr = pygame.transform.flip(curr, True, False)
        return curr
