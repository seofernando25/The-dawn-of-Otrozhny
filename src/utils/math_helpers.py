import math
from typing import Protocol


class HasPosition(Protocol):
    def get_pos(self) -> tuple[float, float]: ...


class SupportsPosition(HasPosition, Protocol):
    fov: float
    angle: float


def clamp(n: float, minn: float, maxn: float) -> float:
    return max(min(maxn, n), minn)


def lerp(v0: float, v1: float, t: float) -> float:
    return (1 - t) * v0 + t * v1


def translate(
    value: float,
    value_min: float,
    value_max: float,
    final_min: float,
    final_max: float,
) -> float:
    """Map a value from one range to another (linear interpolation)."""
    left_length = value_max - value_min
    if left_length == 0:
        return final_min
    scale = (final_max - final_min) / left_length
    offset = final_min - value_min * scale
    return value * scale + offset


def slope(
    aCoord: tuple[float, float], bCoord: tuple[float, float]
) -> tuple[float, float]:
    dy = bCoord[1] - aCoord[1]
    dx = bCoord[0] - aCoord[0]
    return dx, dy


def distance_to(aCoord: tuple[float, float], bCoord: tuple[float, float]) -> float:
    dx, dy = slope(aCoord, bCoord)
    return math.hypot(dx, dy)


def fixed_angle(angle: float) -> float:
    angle = angle % math.radians(360)
    if angle < math.radians(0):
        angle += math.radians(360)
    return angle


def project(
    camera: SupportsPosition, p2: tuple[float, float], table_angle: float
) -> float:
    camera_pos = camera.get_pos()
    dx, dy = slope(camera_pos, p2)

    angle = math.atan2(dy, dx)

    proportional_angle = angle + camera.fov + table_angle + -camera.angle * 2

    a = dx * math.cos(proportional_angle / 2)
    b = dy * math.sin(proportional_angle / 2)
    projected = a + b
    return projected


def points_from_polygon_sides(
    n_sides: int,
    radius: float,
    adjusted: bool = False,
) -> list[tuple[float, float]]:
    segment_size = math.radians(360) / n_sides

    points: list[tuple[float, float]] = []

    for x in range(n_sides):
        angle = segment_size * x
        if adjusted:
            angle += segment_size / 2
        px = math.sin(angle) * radius + radius
        py = radius - math.cos(angle) * radius
        points.append((px, py))
    return points
