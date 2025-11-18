import enum
import math

import pygame

import colors
import levelData
import mathHelpers
from renderer import config as renderer_settings
from entities.base import SpriteEntity

RAY_ANGLE_STEP = renderer_settings.RAY_ANGLE_STEP
VIEWPORT_HEIGHT = renderer_settings.VIEWPORT_HEIGHT


class WallDirection(enum.Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3


def generate_distance_table(entity):
    entity.rayDistanceTable = {}
    entity.entitiesInSight = []

    fov_depth = entity.FOVDepth
    degrees = math.ceil(math.degrees(entity.FOV))
    entity_dir_x = entity.dirX
    enity_dir_y = entity.dirY

    entity_plane_x = entity.planeX
    enity_plane_y = entity.planeY

    entity_px = entity.px
    entity_py = entity.py

    current_map = levelData.require_current_map()
    for w in range(degrees):
        cam_x = ((2 * w) / math.ceil(math.degrees(entity.FOV))) - 1

        entity_plane_x = entity.planeX
        entity_py = entity.py

        ray_dir_x = entity_dir_x + entity_plane_x * cam_x
        ray_dir_y = enity_dir_y + enity_plane_y * cam_x

        if ray_dir_y == 0:
            ray_dir_y = 0.1
        if ray_dir_x == 0:
            ray_dir_x = 0.1

        ray_angle = math.atan2(ray_dir_x, ray_dir_y)

        map_x = int(entity_px)
        map_y = int(entity_py)

        delta_dist_x = abs(1.0 / ray_dir_x)
        delta_dist_y = abs(1.0 / ray_dir_y)

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (entity_px - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - entity_px) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (entity_py - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - entity_py) * delta_dist_y

        hit_wall = False
        steps = 0
        while not hit_wall and steps <= fov_depth:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                steps += 1
                side = 0
            else:
                side_dist_y += delta_dist_y
                steps += 1
                map_y += step_y
                side = 1

            point_x = map_x
            point_y = map_y

            if (point_x < 0
                    or point_x >= current_map.level_width
                    or point_y < 0
                    or point_y >= current_map.level_height
                    or steps >= fov_depth):

                entity.rayDistanceTable[ray_angle] = None
            else:
                if current_map.grid[int(point_x)][int(point_y)]:
                    hit_wall = True
                    wall_col = current_map.grid[int(point_x)][int(point_y)]
                    if side == 0:
                        wallDistance = (map_x - entity_px +
                                        (1.0 - step_x) / 2.0) / ray_dir_x
                    else:
                        wallDistance = (map_y - entity_py +
                                        (1.0 - step_y) / 2.0) / ray_dir_y

                    if side and ray_dir_y < 0:
                        wall_dir = WallDirection.EAST
                    elif side:
                        wall_dir = WallDirection.WEST
                    elif ray_dir_x < 0:
                        wall_dir = WallDirection.SOUTH
                    else:
                        wall_dir = WallDirection.NORTH

                    entity.rayDistanceTable[ray_angle] = (
                        wallDistance,
                        ray_dir_x, ray_dir_y,
                        ray_angle, wall_col,
                        wall_dir)

    _calculate_entities_in_sight(entity)


def _calculate_entities_in_sight(entity):
    current_map = levelData.require_current_map()
    fov_polygons = calculate_fov_polygon(entity)
    for e in current_map.grid_entities:
        if e != entity:
            collided = polygonPointCollision(fov_polygons, e.get_pos())
            if collided:
                ent_list = ((entity.px - e.px) * (entity.px - e.px) +
                            (entity.py - e.py) * (entity.py - e.py))
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

        if (((vc[1] > point[1] and vn[1] < point[1]) or
             (vc[1] < point[1] and vn[1] > point[1]))
                and (point[0] < (vn[0] - vc[0]) * (point[1] - vc[1]) /
                     (vn[1] - vc[1]) + vc[0])):
            collision = not collision
    return collision


def calculate_fov_polygon(entity):
    px = entity.px
    py = entity.py
    entityFovPoints = [(px, py)]

    for ray in entity.rayDistanceTable.items():
        if ray[1] is None:
            continue
        table_step, tableDirX, tableDirY, *_ = ray[1]
        pointX = px + tableDirX * table_step
        pointY = py + tableDirY * table_step
        entityFovPoints.append((pointX, pointY))

    if len(entityFovPoints) > 2:
        return entityFovPoints
    else:
        return [(px, py)] * 3


def render_walls(screen, entity):
    obj_to_draw = {}
    if len(entity.rayDistanceTable) <= 1:
        return
    thickness = screen.get_width() / (len(entity.rayDistanceTable) - 1)
    w_angle = 0
    for ray in entity.rayDistanceTable.items():
        if ray[1] is None:
            w_angle += 1
            continue
        table_step, _, _, _, _, table_side = ray[1]
        wall_projection_distance = table_step
        line_height = abs(screen.get_height() / wall_projection_distance)
        ceiling = -line_height + (screen.get_height() / 2) + entity.angleY
        floor = line_height + (screen.get_height() / 2) + entity.angleY

        wall_color = _get_wall_color(table_side)

        obj_to_draw[(abs(wall_projection_distance), w_angle)] = (
            w_angle, ceiling, floor, wall_color)
        w_angle += RAY_ANGLE_STEP

    entity.entitiesInSight.sort(key=lambda x: x[1])
    for enemy, _ in entity.entitiesInSight:
        if issubclass(type(enemy), SpriteEntity) and enemy != entity:
            dx, dy = mathHelpers.slope(entity.get_pos(), enemy.get_pos())

            projection_disit = (entity.planeX * entity.dirY -
                                entity.dirX * entity.planeY)

            if projection_disit == 0:
                continue

            inverse_projection_dist = 1 / projection_disit

            new_x = inverse_projection_dist * \
                (entity.dirY * dx - entity.dirX * dy)
            new_y = inverse_projection_dist * \
                (-entity.planeY * dx + entity.planeX * dy)

            if abs(new_y) < 0.1:
                continue

            new_pos_x = (entity.FOV / 2) * (1 + new_x / new_y)

            line_height = abs(screen.get_height() / new_y)
            middle = screen.get_height() / 2

            ceiling = -line_height + middle + entity.angleY
            floor = line_height + middle + entity.angleY
            obj_to_draw[(abs(new_y) - 2,
                         math.degrees(new_pos_x))] = (
                math.degrees(new_pos_x),
                ceiling,
                floor,
                enemy)

    sorted_objs = list(obj_to_draw.items())
    sorted_objs.sort(key=lambda x: x[0][0], reverse=True)

    for _, vals in sorted_objs:
        w_angle, ceiling, floor, data = vals
        scaled_width = w_angle * (thickness / 1)
        ceiling = int(ceiling)
        floor = int(floor)
        if isinstance(data, list):
            pygame.draw.line(
                screen, data,
                [int(scaled_width), int(ceiling)],
                [int(scaled_width), int(floor)], math.ceil(thickness))
        if isinstance(data, SpriteEntity):
            scale_multiplier = abs(
                mathHelpers.translate(floor - ceiling, 0,
                                      VIEWPORT_HEIGHT, 0, 4))
            scale_multiplier = max(0, min(scale_multiplier, 5))
            sprite = data.get_sprite(entity)
            if sprite is not None and scale_multiplier > 0:
                scaled_sprite = pygame.transform.scale(
                    sprite,
                    ((50 * sprite.get_height()) // sprite.get_width(), 50))

                target_width = int(scaled_sprite.get_width() * scale_multiplier)
                target_height = int(
                    scaled_sprite.get_height() * scale_multiplier)

                if target_width <= 0 or target_height <= 0:
                    continue

                img = pygame.transform.scale(
                    scaled_sprite,
                    (target_width, target_height))

                screen.blit(img, [
                    int(scaled_width - int(img.get_width() / 1.5)),
                    int(floor - img.get_rect().height)
                ])


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

