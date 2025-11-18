import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE

VIEWPORT_HEIGHT = 320
VIEWPORT_X_OFFSET = 10
VIEWPORT_Y_OFFSET = 30

DEPTH = 40
RAY_ANGLE_STEP = 1

HUD_NUM_OF_CELLS = 5
HUD_CELL_SIZE = 100
HUD_CELL_OFFSET = 10
HUD_CELL_TITLE_OFFSET = 10
HUD_CELL_TITLE_FONT_SIZE = 12
HUD_CELL_OTHER_FONT_SIZE = 12

_SCREEN = None


def get_screen():
    global _SCREEN
    if _SCREEN is None:
        _SCREEN = pygame.display.set_mode(SCREEN_SIZE, FLAGS)
        _SCREEN.set_alpha(None)
    return _SCREEN


def reset_screen():
    """Dispose of the cached screen so tests/demos can recreate it."""
    global _SCREEN
    _SCREEN = None
