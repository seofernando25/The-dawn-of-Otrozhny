# Script used mainly to draw "otherEffects.py" on the screen
# eg: main menu's Sierpinski triangle
import random

from core import colors
from core.backend import get_backend
from renderer.text import blit_surface
from utils import math_helpers
from core.backend.api import GraphicsSurface


# The concept for this class was taken from
# this numberphile video
# https://www.youtube.com/watch?v=kbKtFN71Lfs
class ChaosObject:
    def __init__(self, center: tuple[int, int], size: int, n_sides: int) -> None:
        backend = get_backend()
        self._surface = backend.graphics.create_surface((size, size))
        self._surface.set_colorkey(colors.BLACK)
        self.points: list[tuple[float, float]] = math_helpers.points_from_polygon_sides(
            n_sides, size / 2, adjusted=True
        )
        self.color: tuple[int, int, int] = colors.WHITE
        self.surface_size: int = size
        self.center: tuple[int, int] = center
        self.drawn_points: list[tuple[float, float]] = []
        self.current_point: tuple[float, float] = self.points[0]
        self.drawn_points.append(self.current_point)
        self.updates_before_draw: int = 0

    def draw(self, screen: "GraphicsSurface") -> None:
        backend = get_backend()
        for x in range(self.updates_before_draw):
            point = self.drawn_points[len(self.drawn_points) - 1 - x]
            # Ensure point is exactly 2 elements for type safety
            center: tuple[float, float] = (float(point[0]), float(point[1]))
            backend.graphics.draw_circle(self._surface, self.color, center, 1)
        self.updates_before_draw = 0
        blit_surface(
            screen,
            self._surface,
            (
                self.center[0] - self.surface_size // 2,
                self.center[1] - self.surface_size // 2,
            ),
        )

    def update(self) -> None:
        self.updates_before_draw += 1
        rand_pos = random.randint(0, len(self.points) - 1)
        newPx = math_helpers.lerp(self.current_point[0], self.points[rand_pos][0], 0.5)
        newPy = math_helpers.lerp(self.current_point[1], self.points[rand_pos][1], 0.5)
        self.current_point = (newPx, newPy)
        self.drawn_points.append(self.current_point)


class StarField:
    class Star:
        def __init__(self, parent_width: int, parent_height: int) -> None:
            spread = 3
            self.x: float = float(
                random.randint(-parent_width // spread, parent_width // spread)
            )
            self.y: float = float(
                random.randint(-parent_height // spread, parent_height // spread)
            )
            self.z: float = float(random.randint(1, parent_width))
            self.lastZ: float = self.z

            self.screenX: float = 0.0
            self.screenY: float = 0.0

            self.screenLastX: float = 0.0
            self.screenLastY: float = 0.0

    def __init__(self, size: tuple[int, int]) -> None:
        backend = get_backend()
        self._surface = backend.graphics.create_surface(size)

        self.speed: float = float(random.randint(1, 5))
        width, height = self._surface.get_size()
        self.surface_width: int = width
        self.surface_height: int = height

        self.stars: list[StarField.Star] = []
        for _ in range(250):
            self.stars.append(StarField.Star(size[0], size[1]))

    def update(self, dt: float) -> None:
        for star in self.stars:
            if (
                star.screenX < -5
                or star.screenX > self.surface_width + 5
                or star.screenY < -5
                or star.screenY > self.surface_height + 5
            ):
                star.z = self.surface_width

            star.lastZ = star.z
            star.z -= dt * 10 * self.speed

            if star.z == 0:
                star.z = -0.1

            star.screenX = math_helpers.translate(
                star.x / star.z, 0, 1, 0, self.surface_width
            )
            star.screenY = math_helpers.translate(
                star.y / star.z, 0, 1, 0, self.surface_height
            )
            star.screenX += self.surface_width // 2
            star.screenY += self.surface_height // 2

            star.screenLastX = math_helpers.translate(
                star.x / star.lastZ, 0, 1, 0, self.surface_width
            )
            star.screenLastY = math_helpers.translate(
                star.y / star.lastZ, 0, 1, 0, self.surface_height
            )
            star.screenLastX += self.surface_width // 2
            star.screenLastY += self.surface_height // 2

    def get_surface(self) -> "GraphicsSurface":
        """Get the star field surface."""
        return self._surface

    def draw(self) -> None:
        backend = get_backend()
        _ = self._surface.fill((0, 0, 0))
        for star in self.stars:
            starSize = math_helpers.translate(star.z, self.surface_width, 0, 1, 4)
            if starSize > 8:
                star.z = self.surface_width
            starSize = int(starSize)

            backend.graphics.draw_line(
                self._surface,
                (255, 255, 255),
                (star.screenX, star.screenY),
                (star.screenLastX, star.screenLastY),
                starSize,
            )

    def change_speed(self) -> None:
        num = random.randint(1, 10)
        while abs(self.speed - num) < 3:
            num = random.randint(1, 10)
        self.speed = num
