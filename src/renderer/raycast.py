import enum
import math

import numpy as np
import pygame

from core import colors
from utils import math_helpers
from config import renderer_config
from entities.base import SpriteEntity

RAY_ANGLE_STEP = renderer_config.RAY_ANGLE_STEP
VIEWPORT_HEIGHT = renderer_config.VIEWPORT_HEIGHT


class WallDirection(enum.Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3


def generate_distance_table(entity):
    entity.rayDistanceTable = []
    entity.entitiesInSight = []

    if not hasattr(entity, "context") or entity.context is None:
        raise RuntimeError("Entity requires a GameContext for raycast operations.")
    current_map = entity.context.level
    if current_map is None:
        raise RuntimeError("GameContext.level is not set.")
    grid = current_map.grid_np
    fov_depth = int(math.ceil(entity.FOVDepth))
    degrees = max(1, math.ceil(math.degrees(entity.FOV)))
    inv_degrees = 1.0 / degrees

    entity_dir_x = entity.dirX
    entity_dir_y = entity.dirY
    entity_plane_x = entity.planeX
    entity_plane_y = entity.planeY

    entity_px = entity.px
    entity_py = entity.py

    level_width = current_map.level_width
    level_height = current_map.level_height

    cam_positions = (2.0 * np.arange(degrees, dtype=np.float32) * inv_degrees) - 1.0
    ray_dir_x = entity_dir_x + entity_plane_x * cam_positions
    ray_dir_y = entity_dir_y + entity_plane_y * cam_positions

    ray_dir_x[ray_dir_x == 0] = 1e-6
    ray_dir_y[ray_dir_y == 0] = 1e-6

    map_x = np.full(degrees, int(entity_px), dtype=np.int32)
    map_y = np.full(degrees, int(entity_py), dtype=np.int32)

    delta_dist_x = np.abs(1.0 / ray_dir_x)
    delta_dist_y = np.abs(1.0 / ray_dir_y)

    step_x = np.where(ray_dir_x < 0, -1, 1).astype(np.int8)
    step_y = np.where(ray_dir_y < 0, -1, 1).astype(np.int8)

    side_dist_x = np.where(
        ray_dir_x < 0,
        (entity_px - map_x) * delta_dist_x,
        (map_x + 1.0 - entity_px) * delta_dist_x,
    )
    side_dist_y = np.where(
        ray_dir_y < 0,
        (entity_py - map_y) * delta_dist_y,
        (map_y + 1.0 - entity_py) * delta_dist_y,
    )

    active = np.ones(degrees, dtype=bool)
    hit_mask = np.zeros(degrees, dtype=bool)
    miss_mask = np.zeros(degrees, dtype=bool)
    last_side = np.zeros(degrees, dtype=np.int8)
    steps = np.zeros(degrees, dtype=np.int16)

    wall_distances = np.zeros(degrees, dtype=np.float32)
    wall_tiles = np.zeros(degrees, dtype=np.int16)
    wall_dirs = np.zeros(degrees, dtype=np.int8)

    for _ in range(fov_depth + 1):
        if not active.any():
            break

        step_x_mask = active & (side_dist_x <= side_dist_y)
        step_y_mask = active & ~step_x_mask

        side_dist_x = side_dist_x + delta_dist_x * step_x_mask
        map_x = map_x + step_x * step_x_mask

        side_dist_y = side_dist_y + delta_dist_y * step_y_mask
        map_y = map_y + step_y * step_y_mask

        last_side = np.where(step_x_mask, 0, last_side)
        last_side = np.where(step_y_mask, 1, last_side)

        steps = steps + active.astype(np.int16)

        out_of_bounds = active & (
            (map_x < 0) | (map_x >= level_width) | (map_y < 0) | (map_y >= level_height)
        )
        miss_mask |= out_of_bounds
        active &= ~out_of_bounds

        depth_exceeded = active & (steps >= fov_depth)
        miss_mask |= depth_exceeded
        active &= ~depth_exceeded

        if not active.any():
            break

        sample_mask = active & (step_x_mask | step_y_mask)
        if not sample_mask.any():
            continue

        cell_values = np.zeros(degrees, dtype=np.int16)
        cell_values[sample_mask] = grid[map_x[sample_mask], map_y[sample_mask]]

        hit_cells = sample_mask & (cell_values != 0)
        if not hit_cells.any():
            continue

        hit_indices = np.nonzero(hit_cells)[0]
        hit_mask[hit_indices] = True
        active[hit_indices] = False
        wall_tiles[hit_indices] = cell_values[hit_indices]

        sides = last_side[hit_indices]

        dist_x = (
            map_x[hit_indices] - entity_px + (1.0 - step_x[hit_indices]) / 2.0
        ) / ray_dir_x[hit_indices]
        dist_y = (
            map_y[hit_indices] - entity_py + (1.0 - step_y[hit_indices]) / 2.0
        ) / ray_dir_y[hit_indices]
        wall_distances[hit_indices] = np.where(sides == 0, dist_x, dist_y)

        wall_dirs[hit_indices] = np.where(
            sides == 1,
            np.where(
                ray_dir_y[hit_indices] < 0,
                WallDirection.EAST.value,
                WallDirection.WEST.value,
            ),
            np.where(
                ray_dir_x[hit_indices] < 0,
                WallDirection.SOUTH.value,
                WallDirection.NORTH.value,
            ),
        )

    miss_mask |= active

    ray_table = []
    for idx in range(degrees):
        if hit_mask[idx]:
            ray_table.append(
                (
                    float(wall_distances[idx]),
                    float(ray_dir_x[idx]),
                    float(ray_dir_y[idx]),
                    int(wall_tiles[idx]),
                    WallDirection(int(wall_dirs[idx])),
                )
            )
        else:
            ray_table.append(None)

    entity.rayDistanceTable = ray_table

    _calculate_entities_in_sight(entity)


def _calculate_entities_in_sight(entity):
    if not hasattr(entity, "context") or entity.context is None:
        raise RuntimeError("Entity requires a GameContext for raycast operations.")
    current_map = entity.context.level
    if current_map is None:
        raise RuntimeError("GameContext.level is not set.")
    fov_polygons = calculate_fov_polygon(entity)
    for e in current_map.grid_entities:
        if e != entity:
            collided = polygonPointCollision(fov_polygons, e.get_pos())
            if collided:
                ent_list = (entity.px - e.px) * (entity.px - e.px) + (
                    entity.py - e.py
                ) * (entity.py - e.py)
                entity.entitiesInSight.append((e, ent_list))


def polygonPointCollision(vertices, p):
    collision = False
    nextP = 0
    point = [p[0], p[1]]
    vert_len = len(vertices)

    for current in range(vert_len):
        nextP += 1

        if nextP == vert_len:
            nextP = 0

        vc = list(vertices[current])
        vn = list(vertices[nextP])

        if (
            (vc[1] > point[1] and vn[1] < point[1])
            or (vc[1] < point[1] and vn[1] > point[1])
        ) and (
            point[0] < (vn[0] - vc[0]) * (point[1] - vc[1]) / (vn[1] - vc[1]) + vc[0]
        ):
            collision = not collision
    return collision


def calculate_fov_polygon(entity):
    px = entity.px
    py = entity.py
    entityFovPoints = [(px, py)]

    for ray in entity.rayDistanceTable:
        if ray is None:
            continue
        table_step, tableDirX, tableDirY, *_ = ray
        pointX = px + tableDirX * table_step
        pointY = py + tableDirY * table_step
        entityFovPoints.append((pointX, pointY))

    if len(entityFovPoints) > 2:
        return entityFovPoints
    else:
        return [(px, py)] * 3


def render_walls(screen, entity):
    ray_table = entity.rayDistanceTable
    if len(ray_table) <= 1:
        return

    screen_height = screen.get_height()
    screen_width = screen.get_width()
    half_height = screen_height / 2
    thickness = screen_width / max(len(ray_table), 1)

    draw_commands = []

    for idx, ray in enumerate(ray_table):
        if ray is None:
            continue
        wall_distance, _, _, _, table_side = ray
        if wall_distance == 0:
            continue
        line_height = abs(screen_height / wall_distance)
        ceiling = -line_height + half_height + entity.angleY
        floor = line_height + half_height + entity.angleY
        wall_color = _get_wall_color(table_side)
        draw_commands.append(
            (abs(wall_distance), "wall", idx * thickness, ceiling, floor, wall_color)
        )

    entity.entitiesInSight.sort(key=lambda x: x[1])
    projection_disit = entity.planeX * entity.dirY - entity.dirX * entity.planeY
    if projection_disit != 0:
        inverse_projection_dist = 1 / projection_disit
        for enemy, _ in entity.entitiesInSight:
            if not issubclass(type(enemy), SpriteEntity) or enemy == entity:
                continue

            dx, dy = math_helpers.slope(entity.get_pos(), enemy.get_pos())
            new_x = inverse_projection_dist * (entity.dirY * dx - entity.dirX * dy)
            new_y = inverse_projection_dist * (-entity.planeY * dx + entity.planeX * dy)

            if abs(new_y) < 0.1:
                continue

            sprite_distance = abs(new_y) - 2
            line_height = abs(screen_height / new_y)
            ceiling = -line_height + half_height + entity.angleY
            floor = line_height + half_height + entity.angleY
            screen_x = (screen_width / 2) * (1 + new_x / new_y)
            draw_commands.append(
                (sprite_distance, "sprite", screen_x, ceiling, floor, enemy)
            )

    draw_commands.sort(key=lambda cmd: cmd[0], reverse=True)

    for _, cmd_type, pos_x, ceiling, floor, data in draw_commands:
        ceiling = int(ceiling)
        floor = int(floor)
        if cmd_type == "wall":
            pygame.draw.line(
                screen,
                data,
                [int(pos_x), int(ceiling)],
                [int(pos_x), int(floor)],
                max(1, math.ceil(thickness)),
            )
        elif isinstance(data, SpriteEntity):
            scale_multiplier = abs(
                math_helpers.translate(floor - ceiling, 0, VIEWPORT_HEIGHT, 0, 4)
            )
            scale_multiplier = max(0, min(scale_multiplier, 5))
            sprite = data.get_sprite(entity)
            if sprite is None or scale_multiplier <= 0:
                continue

            scaled_sprite = pygame.transform.scale(
                sprite, ((50 * sprite.get_height()) // sprite.get_width(), 50)
            )
            target_width = int(scaled_sprite.get_width() * scale_multiplier)
            target_height = int(scaled_sprite.get_height() * scale_multiplier)

            if target_width <= 0 or target_height <= 0:
                continue

            img = pygame.transform.scale(scaled_sprite, (target_width, target_height))
            screen.blit(
                img,
                [int(pos_x - img.get_width() / 2), int(floor - img.get_rect().height)],
            )


def _get_wall_color(table_side):
    wall_color = colors.RED
    if table_side == WallDirection.NORTH:
        wall_color = list(colors.GRAY_VARIATION_1)
    if table_side == WallDirection.SOUTH:
        wall_color = list(colors.GRAY_VARIATION_2)
    if table_side == WallDirection.EAST:
        wall_color = list(colors.GRAY_VARIATION_3)
    if table_side == WallDirection.WEST:
        wall_color = list(colors.GRAY_VARIATION_4)
    return wall_color
