# Color definitions and functions

#Basic Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
TRANSPARENT = (0,0,0,0)

#Color Mixture
DIM_RED = (200, 0, 0)
YELLOW = (255, 255, 0)
YELLOW_WHITE = (255, 255, 144)
NAVY_BLUE = (0,0, 144)
BRIGHT_BLUE = (100,100, 255)
ACCENTUADED_BLUE = (25, 25, 255)
PINK = (255, 0, 255)
CYAN = (0, 255, 255)
MAROON = (128, 0, 0)
GRAY = (144,144,144)
DARK_GRAY = (100,100,100)
ALMOST_BLACK = (25,25,25)

#I ended up using only these colors for the wall by desing
GRAY_VARIATION_1 = (153,153,153)
GRAY_VARIATION_2 = (119,119,119)
GRAY_VARIATION_3 = (85,85,85)
GRAY_VARIATION_4 = (160,160,160)

def truncate_color(color):
    new_color = []
    for index, luminosity in enumerate(color):
        if luminosity < 0:
            luminosity = 0 
        if luminosity > 255:
            luminosity = 255

        new_color.append(luminosity)
    return new_color

def divide(color , n):
    new_color = []
    for index, luminosity in enumerate(color):
        new_color.append(int(color[index] / n))
    return truncate_color(new_color)

def multiply(color , n):
    new_color = []
    for index, luminosity in enumerate(color):
        new_color.append(int(color[index] * n))
    return truncate_color(new_color)

def lerp_color(color1, color2, t):
    import mathHelpers
    new_color = []
    for index, luminosity in enumerate(color1):
        new_color.append(mathHelpers.lerp( int(color1[index]), color2[index], t))
    return truncate_color(new_color)