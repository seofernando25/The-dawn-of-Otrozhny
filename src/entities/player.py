from config import PLAYER_CONFIG, renderer_config
from .base import SpriteAgent


class Player(SpriteAgent):
    """Player entity controlled by InputSystem."""

    def __init__(self, start_pos: tuple[float, float], *, context=None):
        super().__init__(
            start_pos,
            float(PLAYER_CONFIG["fov_degrees"]),
            float(PLAYER_CONFIG["move_speed"]),
            float(renderer_config.DEPTH),
            str(PLAYER_CONFIG["sprite_pack"]),
            context=context,
        )
        self.mouseEnable: bool = False
        self.cameraYawSens: float = float(PLAYER_CONFIG["camera_yaw_sensitivity"])
        self.cameraPitchSens: float = float(PLAYER_CONFIG["camera_pitch_sensitivity"])
        self.keys: int = 0
