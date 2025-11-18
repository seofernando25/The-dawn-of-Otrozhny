"""
Renderer configuration constants.

All renderer-related configuration values are centralized here.
"""

import pygame

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Pygame display flags
FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE

# Viewport settings
VIEWPORT_HEIGHT = 320
VIEWPORT_X_OFFSET = 10
VIEWPORT_Y_OFFSET = 30

# Raycasting settings
DEPTH = 40
RAY_ANGLE_STEP = 1

# HUD settings
HUD_NUM_OF_CELLS = 5
HUD_CELL_SIZE = 100
HUD_CELL_OFFSET = 10
HUD_CELL_TITLE_OFFSET = 10
HUD_CELL_TITLE_FONT_SIZE = 12
HUD_CELL_OTHER_FONT_SIZE = 12

