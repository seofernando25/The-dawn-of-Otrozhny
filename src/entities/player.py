import pygame
import pygame.constants as pyConst

from config import PLAYER_CONFIG
from renderer import config as renderer_settings
from .base import SpriteAgent
from physics import movement


class Player(SpriteAgent):
    def __init__(self, start_pos, *, context=None):
        super().__init__(
            start_pos,
            PLAYER_CONFIG["fov_degrees"],
            PLAYER_CONFIG["move_speed"],
            renderer_settings.DEPTH,
            PLAYER_CONFIG["sprite_pack"],
            context=context,
        )
        self.mouseEnable = False
        self.cameraYawSens = PLAYER_CONFIG["camera_yaw_sensitivity"]
        self.cameraPitchSens = PLAYER_CONFIG["camera_pitch_sensitivity"]
        self.keys = 0

    def update(self, dt, events):
        get_input(self, dt, events)
        return super().update(dt, events)


def get_input(entity, dt, events):
    deltaTime = dt

    kb = pygame.key.get_pressed()
    for event in events:
        if event.type == pyConst.KEYDOWN:
            if event.key == pyConst.K_ESCAPE:
                pygame.mouse.set_pos(
                    [
                        renderer_settings.SCREEN_WIDTH // 2,
                        renderer_settings.SCREEN_HEIGHT // 2,
                    ]
                )
                entity.mouseEnable = not entity.mouseEnable

    pygame.mouse.set_visible(not entity.mouseEnable)
    pygame.event.set_grab(entity.mouseEnable)
    screen_size = None
    if entity.context is not None and entity.context.screen is not None:
        screen_size = entity.context.screen.get_size()
    newPx, newPy = movement.get_input_movement(
        entity,
        deltaTime,
        kb,
        mouse_enabled=entity.mouseEnable,
        screen_size=screen_size,
    )

    entity.move(newPx, newPy, deltaTime)
