# Script used mainly to draw "otherEffects.py" on the screen
# eg: main menu's Sierpinski triangle
import random

from core import colors
import pygame
from utils import math_helpers


# The concept for this class was taken from
# this numberphile video
# https://www.youtube.com/watch?v=kbKtFN71Lfs
class ChaosObject(pygame.Surface):
    def __init__(self, center, size, n_sides):
        super().__init__((size, size))
        self.set_colorkey(colors.BLACK)
        self.points = math_helpers.points_from_polygon_sides(
            n_sides, size / 2, adjusted=True
        )
        self.color = colors.WHITE
        self.surface_size = size
        self.center = center
        self.n_of_itterations = 0
        self.drawn_points = []
        self.current_point = self.points[0]
        self.drawn_points.append(self.current_point)
        self.updates_before_draw = 0

    def draw(self, screen):
        for x in range(self.updates_before_draw):
            point = self.drawn_points[len(self.drawn_points) - 1 - x]
            pygame.draw.circle(self, self.color, tuple([int(x) for x in point]), 1)
        self.updates_before_draw = 0
        screen.blit(
            self,
            (
                self.center[0] - self.surface_size // 2,
                self.center[1] - self.surface_size // 2,
            ),
        )

    def update(self):
        self.updates_before_draw += 1
        self.n_of_itterations += 1
        rand_pos = random.randint(0, len(self.points) - 1)
        newPx = math_helpers.lerp(self.current_point[0], self.points[rand_pos][0], 0.5)
        newPy = math_helpers.lerp(self.current_point[1], self.points[rand_pos][1], 0.5)
        self.current_point = (newPx, newPy)
        self.drawn_points.append(self.current_point)


class ChaosSnowFlake(ChaosObject):
    def __init__(self, center, size):
        super().__init__(center, size, 5)
        self.previous = None

    def update(self):
        rand_pos = random.randint(0, len(self.points) - 1)
        while rand_pos == self.previous:
            rand_pos = random.randint(0, len(self.points) - 1)

        newPx = math_helpers.lerp(self.current_point[0], self.points[rand_pos][0], 0.5)
        newPy = math_helpers.lerp(self.current_point[1], self.points[rand_pos][1], 0.5)
        self.current_point = (newPx, newPy)
        self.drawn_points.append(self.current_point)
        self.previous = rand_pos


class StarField(pygame.Surface):
    class Star:
        def __init__(self, parent_width, parent_height):
            spread = 3
            self.x = random.randint(-parent_width // spread, parent_width // spread)
            self.y = random.randint(-parent_height // spread, parent_height // spread)
            self.z = random.randint(1, parent_width)
            self.lastZ = self.z

            self.screenX = 0
            self.screenY = 0

            self.screenLastX = 0
            self.screenLastY = 0

    def __init__(self, size):
        super().__init__(size)

        self.speed = random.randint(1, 5)
        self.surface_width = self.get_width()
        self.surface_height = self.get_height()

        self.stars = []
        for x in range(250):
            self.stars.append(StarField.Star(size[0], size[1]))

    def update(self, dt):
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

    def draw(self):
        self.fill((0, 0, 0))
        for star in self.stars:
            starSize = math_helpers.translate(star.z, self.surface_width, 0, 1, 4)
            if starSize > 8:
                star.z = self.surface_width
            starSize = int(starSize)

            pygame.draw.line(
                self,
                (255, 255, 255),
                (star.screenX, star.screenY),
                (star.screenLastX, star.screenLastY),
                starSize,
            )

    def change_speed(self):
        num = random.randint(1, 10)
        while abs(self.speed - num) < 3:
            num = random.randint(1, 10)
        self.speed = num

