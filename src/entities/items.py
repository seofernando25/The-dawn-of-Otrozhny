import math

import mathHelpers
from .base import SpriteEntity
from .player import Player


class Collectible(SpriteEntity):
    def __init__(self, start_pos):
        super().__init__(start_pos, "Collectible")
        self.collected = False

    def update(self, dt, events):
        if not self.collected:
            import levelData
            player = Player.require_instance()
            current_map = levelData.require_current_map()
            dist = mathHelpers.distance_to(self.get_pos(), player.get_pos())
            if dist < 0.5:
                current_map.num_of_collected += 1
                self.collected = True
                self.agent_pack_name = ""


class Gate(SpriteEntity):
    def __init__(self, start_pos):
        super().__init__(start_pos, "Gate")
        self.open = False

    def update(self, dt, events):
        if not self.open:
            player = Player.require_instance()
            dist = mathHelpers.distance_to(self.get_pos(), player.get_pos())
            if dist < 0.5:
                if player.keys > 0:
                    player.keys -= 1
                    self.open = True
                    self.agent_pack_name = ""
            elif dist < 1 and player.keys == 0:
                knockback_dx, knockback_dy = mathHelpers.slope(
                    self.get_pos(), player.get_pos())
                knockback_length = math.hypot(knockback_dx, knockback_dy)
                if knockback_length > 0:
                    strength = 0.5
                    player.move(
                        (knockback_dx / knockback_length) * strength,
                        (knockback_dy / knockback_length) * strength, dt)


class Key(SpriteEntity):
    def __init__(self, start_pos):
        super().__init__(start_pos, "Key")
        self.collected = False

    def update(self, dt, events):
        if not self.collected:
            player = Player.require_instance()
            dist = mathHelpers.distance_to(self.get_pos(), player.get_pos())
            if dist < 0.5:
                player.keys += 1
                self.collected = True
                self.agent_pack_name = ""
