import math

import pygame
import pygame.constants as pyConst

import mathHelpers
from renderer import config as renderer_settings
from .base import SpriteAgent

testGlobalVar = 0


class Player(SpriteAgent):
    instance = None

    def __init__(self, start_pos):
        super().__init__(start_pos, 90, 2, renderer_settings.DEPTH, "enemyIdle")
        Player.instance = self
        self.mouseEnable = False
        self.cameraYawSens = 2
        self.cameraPitchSens = 360
        self.keys = 0

    def update(self, dt, events):
        get_input(self, dt, events)
        return super().update(dt, events)

    @classmethod
    def require_instance(cls) -> "Player":
        if cls.instance is None:
            raise RuntimeError("Player.instance is not initialized")
        return cls.instance


def get_input(entity, dt, events):
    global testGlobalVar
    deltaTime = dt

    kb = pygame.key.get_pressed()
    for event in events:
        if event.type == pyConst.KEYDOWN:
            if event.key == pyConst.K_ESCAPE:
                pygame.mouse.set_pos([
                    renderer_settings.SCREEN_WIDTH // 2,
                    renderer_settings.SCREEN_HEIGHT // 2,
                ])
                entity.mouseEnable = not entity.mouseEnable

    pygame.mouse.set_visible(not entity.mouseEnable)
    pygame.event.set_grab(entity.mouseEnable)
    if entity.mouseEnable:
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_pos([
            renderer_settings.SCREEN_WIDTH // 2,
            renderer_settings.SCREEN_HEIGHT // 2,
        ])
        mouseDeltaX = (mouse_pos[0] - renderer_settings.SCREEN_WIDTH // 2)
        mouseDeltaY = (mouse_pos[1] - renderer_settings.SCREEN_HEIGHT // 2)
        entity.rotate(-entity.cameraYawSens * 0.05 * deltaTime * mouseDeltaX)

        entity.angleY -= (
            0.05 * deltaTime * entity.cameraPitchSens * mouseDeltaY)

    if kb[pyConst.K_LEFT]:
        entity.rotate(entity.cameraYawSens * deltaTime)

    if kb[pyConst.K_RIGHT]:
        entity.rotate(-entity.cameraYawSens * deltaTime)

    if kb[pyConst.K_UP]:
        entity.angleY += entity.cameraPitchSens * deltaTime

    if kb[pyConst.K_DOWN]:
        entity.angleY -= entity.cameraPitchSens * deltaTime

    newPx = 0
    newPy = 0
    angle = math.atan2(-entity.dirY, entity.dirX)

    entity.angleY = mathHelpers.clamp(
        entity.angleY,
        -renderer_settings.VIEWPORT_HEIGHT,
        renderer_settings.VIEWPORT_HEIGHT,
    )

    if kb[pyConst.K_d]:
        newPx -= math.sin(angle) * 2 * deltaTime
        newPy -= math.cos(angle) * 2 * deltaTime

    if kb[pyConst.K_a]:
        newPx += math.sin(angle) * entity.moveSpeed * deltaTime
        newPy += math.cos(angle) * entity.moveSpeed * deltaTime

    if kb[pyConst.K_w]:
        newPx += math.cos(angle) * entity.moveSpeed * deltaTime
        newPy -= math.sin(angle) * entity.moveSpeed * deltaTime

    if kb[pyConst.K_s]:
        newPx -= math.cos(angle) * entity.moveSpeed * deltaTime
        newPy += math.sin(angle) * entity.moveSpeed * deltaTime

    if kb[pyConst.K_n]:
        testGlobalVar -= 1 * deltaTime
        print(testGlobalVar)

    if kb[pyConst.K_m]:
        testGlobalVar += 1 * deltaTime
        print(testGlobalVar)

    entity.move(newPx, newPy, deltaTime)

