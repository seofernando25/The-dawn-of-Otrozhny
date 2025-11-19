# Functions to draw text on the screen
import os
import pygame
from core import colors

DEFAULT_FONT_SIZE = 8

ColorValue = tuple[int, int, int] | list[int] | str
Coordinate = float

font_cache: dict[int, pygame.font.Font] = {}
# Get the src directory (parent of renderer)
dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
FONT_NAME = "ff.ttf"
FONT_PATH = os.path.join(dir_path, "assets", "fonts", FONT_NAME)


def text_object(
    text: str, font: pygame.font.Font, color: ColorValue = colors.WHITE
) -> tuple[pygame.Surface, pygame.Rect]:
    text_surface = font.render(str(text), True, color)
    return text_surface, text_surface.get_rect()


def _get_font(size: int) -> pygame.font.Font:
    if size not in font_cache:
        font_cache[size] = pygame.font.Font(FONT_PATH, size)
    return font_cache[size]


def message_display_L(
    screen: pygame.Surface,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int = DEFAULT_FONT_SIZE,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.topleft = (x, y)
    screen.blit(text_surf, text_rect)


def message_display_R(
    screen: pygame.Surface,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int = DEFAULT_FONT_SIZE,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.topright = (x, y)
    screen.blit(text_surf, text_rect)


def message_display_MB(
    screen: pygame.Surface,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int = DEFAULT_FONT_SIZE,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.midbottom = (x, y)
    screen.blit(text_surf, text_rect)


def message_display_MT(
    screen: pygame.Surface,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.midtop = (x, y)
    screen.blit(text_surf, text_rect)


def message_display(
    screen: pygame.Surface,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.center = (x, y)
    screen.blit(text_surf, text_rect)


def truncline(text: str, maxwidth: int, font: pygame.font.Font) -> tuple[int, int, str]:
    text = str(text)
    real = len(text)
    stext = text
    text_width = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while text_width > maxwidth:
        a = a + 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        text_width = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text: str, pixel_max_width: int, size: int) -> list[str]:
    """Wrap text to fit within a pixel width."""
    done = 0
    wrapped: list[str] = []
    if size in font_cache:
        font = font_cache[size]
    else:
        font = pygame.font.Font(FONT_PATH, size)
    while not done:
        nl, done, stext = truncline(text, pixel_max_width, font)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped
