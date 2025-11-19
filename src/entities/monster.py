import math
import random
from utils import math_helpers
from config import ENEMY_CONFIG, DAMAGE_CONFIG, SOUND_CONFIG
from .enemy import Enemy


class Monster(Enemy):
    """Enemy that can attack the player and make sounds."""

    def __init__(self, start_pos, patrolPoint=None, *, context=None):
        super().__init__(start_pos, patrolPoint=patrolPoint, context=context)

    def update(self, dt):
        """Update monster behavior including attacks and sounds."""
        super().update(dt)

        dist_to_player = math.inf
        if self.target is not None:
            player = self._player()
            dist_to_player = math_helpers.distance_to(self.get_pos(), player.get_pos())
            attack_dist = ENEMY_CONFIG["attack_distance"]
            if isinstance(attack_dist, (int, float)):
                if (
                    self.target is player
                    and dist_to_player < attack_dist
                    and self.canSeePlayer
                ):
                    self.attack(player, dt)
                if (
                    self.target is player
                    and dist_to_player < attack_dist
                    and not self.canSeePlayer
                ):
                    self.look_at(player, dt)
        sound_dist = ENEMY_CONFIG["sound_trigger_distance"]
        if isinstance(sound_dist, (int, float)) and dist_to_player < sound_dist:
            enemy_state = self._enemy_state()
            self.play_sound(dist_to_player, enemy_state.status.name)

    def play_sound(self, distance, flag, force=False):
        """Play a sound effect with distance-based volume."""
        context = self.requires_context()
        if context.audio is None:
            return

        volume = math_helpers.translate(
            distance,
            SOUND_CONFIG["volume_distance_min"],
            SOUND_CONFIG["volume_distance_max"],
            SOUND_CONFIG["volume_max"],
            SOUND_CONFIG["volume_min"],
        )
        levels = (volume, volume)
        context.audio.play_sound(
            flag,
            pack=self.agent_pack_name,
            volume=levels,
            force=force,
        )

    def attack(self, target, dt):
        """Attack a target entity."""
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
