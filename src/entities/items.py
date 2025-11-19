from utils import math_helpers
from config import COLLISION_DISTANCES
from .base import SpriteEntity


class Collectible(SpriteEntity):
    def __init__(self, start_pos, *, context=None):
        super().__init__(start_pos, "collectible", context=context)
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
        super().__init__(start_pos, "gate", context=context)
        self.open = False
        self._grid_pos: tuple[int, int] | None = None

    def set_context(self, context):
        super().set_context(context)
        self._grid_pos = (int(self.px), int(self.py))
        self._apply_grid_state()

    def update(self, dt):
        if not self.open:
            player = self._player()
            if self._player_can_interact(player):
                if player.keys > 0:
                    player.keys -= 1
                    self.open = True
                    self.agent_pack_name = ""
                    self._apply_grid_state()

    def _apply_grid_state(self):
        if self.context is None or self._grid_pos is None:
            return
        current_map = self._current_map()
        grid_x, grid_y = self._grid_pos
        if not (
            0 <= grid_x < current_map.level_width
            and 0 <= grid_y < current_map.level_height
        ):
            return
        current_map.grid[grid_x][grid_y] = 0 if self.open else 2

    def _player_can_interact(self, player) -> bool:
        gate_pos = self.get_pos()
        player_pos = player.get_pos()
        dist = math_helpers.distance_to(gate_pos, player_pos)
        if dist < COLLISION_DISTANCES["gate_interaction"]:
            return True
        gate_tile = (int(gate_pos[0]), int(gate_pos[1]))
        player_tile = (int(player_pos[0]), int(player_pos[1]))
        return (
            abs(gate_tile[0] - player_tile[0]) <= 1
            and abs(gate_tile[1] - player_tile[1]) <= 1
        )


class Key(SpriteEntity):
    def __init__(self, start_pos, *, context=None):
        super().__init__(start_pos, "key", context=context)
        self.collected = False

    def update(self, dt):
        if not self.collected:
            player = self._player()
            dist = math_helpers.distance_to(self.get_pos(), player.get_pos())
            if dist < COLLISION_DISTANCES["key_pickup"]:
                player.keys += 1
                self.collected = True
                self.agent_pack_name = ""
