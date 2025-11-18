from config import PLAYER_CONFIG, renderer_config
from .base import SpriteAgent


class Player(SpriteAgent):
    """Player entity controlled by InputSystem."""
    
    def __init__(self, start_pos, *, context=None):
        super().__init__(
            start_pos,
            PLAYER_CONFIG["fov_degrees"],
            PLAYER_CONFIG["move_speed"],
            renderer_config.DEPTH,
            PLAYER_CONFIG["sprite_pack"],
            context=context,
        )
        self.mouseEnable = False
        self.cameraYawSens = PLAYER_CONFIG["camera_yaw_sensitivity"]
        self.cameraPitchSens = PLAYER_CONFIG["camera_pitch_sensitivity"]
        self.keys = 0
