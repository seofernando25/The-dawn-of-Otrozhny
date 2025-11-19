# Color definitions and functions

Coordinate = float
ColorValue = tuple[int, int, int] | list[int] | str

# Basic Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
# Color Mixture
YELLOW = (255, 255, 0)
YELLOW_WHITE = (255, 255, 144)
NAVY_BLUE = (0, 0, 144)
ACCENTUADED_BLUE = (25, 25, 255)
PINK = (255, 0, 255)
MAROON = (128, 0, 0)
GRAY = (144, 144, 144)
DARK_GRAY = (100, 100, 100)
ALMOST_BLACK = (25, 25, 25)

GRAY_VARIATION_1 = (153, 153, 153)
GRAY_VARIATION_2 = (119, 119, 119)
GRAY_VARIATION_3 = (85, 85, 85)
GRAY_VARIATION_4 = (160, 160, 160)


def truncate_color(color: list[int] | tuple[int, ...]) -> list[int]:
    new_color: list[int] = []
    for luminosity in color:
        if luminosity < 0:
            luminosity = 0
        if luminosity > 255:
            luminosity = 255

        new_color.append(luminosity)
    return new_color


def multiply(color: list[int] | tuple[int, ...], n: int | float) -> list[int]:
    new_color: list[int] = []
    for index in range(len(color)):
        new_color.append(int(color[index] * n))
    return truncate_color(new_color)
