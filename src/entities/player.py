import pygame
import pygame.constants as pyConst

from renderer import config as renderer_settings
from .base import SpriteAgent
from physics import movement

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
    newPx, newPy = movement.get_input_movement(
        entity, deltaTime, kb, mouse_enabled=entity.mouseEnable)

    if kb[pyConst.K_n]:
        testGlobalVar -= 1 * deltaTime
        print(testGlobalVar)

    if kb[pyConst.K_m]:
        testGlobalVar += 1 * deltaTime
        print(testGlobalVar)

    entity.move(newPx, newPy, deltaTime)

