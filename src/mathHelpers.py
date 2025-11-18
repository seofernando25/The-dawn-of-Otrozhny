# Basic math functions
import math


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

# Linear interpolation
# Sauce: https://en.wikipedia.org/wiki/Linear_interpolation#Programming_language_support


def lerp(v0, v1, t) -> float:
    return (1 - t) * v0 + t * v1

# Scales one number to another


def translate(value, value_min, value_max, final_min, final_max):
    left_lenght = value_max - value_min
    right_lenght = final_max - final_min
    scaled_value = float(value - value_min) / float(left_lenght)
    return final_min + (scaled_value * right_lenght)

# y2 - y1 over
# x2 - x1


def slope(aCoord, bCoord):
    dy = bCoord[1] - aCoord[1]
    dx = bCoord[0] - aCoord[0]
    return dx, dy


def distance_to(aCoord, bCoord):
    dx, dy = slope(aCoord, bCoord)
    return math.hypot(dx, dy)

# Wraps angle to 360 deg


def fixed_angle(angle):
    angle = angle % math.radians(360)
    if angle < math.radians(0):
        angle += math.radians(360)
    return angle


def project(camera, p2, table_angle):
    camera_pos = camera.get_pos()
    dx, dy = slope(camera_pos, p2)

    angle = math.atan2(dy, dx)

    proportional_angle = angle + camera.FOV + table_angle + -camera.angle * 2

    a = dx * math.cos(proportional_angle/2)
    b = dy * math.sin(proportional_angle/2)
    projected = a + b
    return projected

# Simple math function to create polygons


def points_from_polygon_sides(n_sides, radius, adjusted=False):
    segment_size = math.radians(360) / n_sides

    points = []

    for x in range(n_sides):
        # PS: I add the radius later so the points wont be negative
        px = math.sin(segment_size * x) * radius + radius
        py = math.cos(segment_size * x) * radius + radius
        points.append((px, py))
    return points
