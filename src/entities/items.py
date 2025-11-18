import math

from utils import math_helpers
from config import COLLISION_DISTANCES
from .base import SpriteEntity


class Collectible(SpriteEntity):
    def __init__(self, start_pos, *, context=None):
        super().__init__(start_pos, "Collectible", context=context)
        self.collected = False

    def update(self, dt):
        if not self.collected:
            player = self._player()
            current_map = self._current_map()
            dist = math_helpers.distance_to(self.get_pos(), player.get_pos())
            if dist < COLLISION_DISTANCES["collectible_pickup"]:
                current_map.num_of_collected += 1
                self.collected = True
                self.agent_pack_name = ""


class Gate(SpriteEntity):
    def __init__(self, start_pos, *, context=None):
        super().__init__(start_pos, "Gate", context=context)
        self.open = False

    def update(self, dt):
        if not self.open:
            player = self._player()
            dist = math_helpers.distance_to(self.get_pos(), player.get_pos())
            if dist < COLLISION_DISTANCES["gate_interaction"]:
                if player.keys > 0:
                    player.keys -= 1
                    self.open = True
                    self.agent_pack_name = ""
            elif dist < COLLISION_DISTANCES["gate_knockback"] and player.keys == 0:
                knockback_dx, knockback_dy = math_helpers.slope(
                    self.get_pos(), player.get_pos()
                )
                knockback_length = math.hypot(knockback_dx, knockback_dy)
                if knockback_length > 0:
                    strength = COLLISION_DISTANCES["gate_knockback_strength"]
                    player.move(
                        (knockback_dx / knockback_length) * strength,
                        (knockback_dy / knockback_length) * strength,
                        dt,
                    )


class Key(SpriteEntity):
    def __init__(self, start_pos, *, context=None):
        super().__init__(start_pos, "Key", context=context)
        self.collected = False

    def update(self, dt):
        if not self.collected:
            player = self._player()
            dist = math_helpers.distance_to(self.get_pos(), player.get_pos())
            if dist < COLLISION_DISTANCES["key_pickup"]:
                player.keys += 1
                self.collected = True
                self.agent_pack_name = ""
