# Functions to draw text on the screen
import os
from typing import TYPE_CHECKING, TypeAlias

from core import colors
from core.backend import get_backend
from core.backend.api import GraphicsSurface

if TYPE_CHECKING:
    from core.backend.api import Font

SurfaceLike: TypeAlias = GraphicsSurface

DEFAULT_FONT_SIZE = 8

ColorValue = tuple[int, int, int] | list[int] | str
Coordinate = float

font_cache: dict[int, "Font"] = {}
# Get the src directory (parent of renderer)
dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
FONT_NAME = "ff.ttf"
FONT_PATH = os.path.join(dir_path, "assets", "fonts", FONT_NAME)


def text_object(
    text: str, font: "Font", color: ColorValue = colors.WHITE
) -> tuple["GraphicsSurface", tuple[tuple[int, int], tuple[int, int]]]:  # Returns (surface, rect)
    text_surface = font.render(str(text), True, color)
    # Since we can't easily get the rect from our abstract surface, we'll make a simple rect
    width, height = font.size(str(text))
    return text_surface, ((0, 0), (width, height))


def _get_font(size: int) -> "Font":
    if size not in font_cache:
        backend = get_backend()
        font_cache[size] = backend.graphics.load_font(FONT_PATH, size)
    return font_cache[size]


def _blit_surface(
    target: SurfaceLike,
    source: SurfaceLike,
    dest: tuple[Coordinate, Coordinate],
) -> None:
    """
    Blit helper that supports both GraphicsSurface instances and raw pygame surfaces.
    Also handles HudButton objects by extracting their _surface.
    """
    import pygame
    from core.backend.pygame_backend import PygameGraphicsSurface
    
    # Handle HudButton objects by extracting their _surface
    if hasattr(source, '_surface') and not isinstance(source, PygameGraphicsSurface):
        # It's likely a HudButton or similar wrapper
        source = source._surface  # type: ignore[attr-defined]
    
    # Handle case where target is a raw pygame.Surface (for backward compatibility)
    if isinstance(target, pygame.Surface):
        if isinstance(source, PygameGraphicsSurface):
            target.blit(source._surface, dest)  # type: ignore[attr-defined]
        elif isinstance(source, pygame.Surface):
            target.blit(source, dest)
        else:
            raise TypeError(
                f"Unsupported source surface type {type(source)} for pygame target"
            )
        return
    
    # Both are GraphicsSurface - use the abstraction
    target.blit(source, dest)


def message_display_L(
    screen: SurfaceLike,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int = DEFAULT_FONT_SIZE,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    # We'll simulate the rect positioning by blitting at adjusted coordinates
    _blit_surface(screen, text_surf, (x, y))


def message_display_R(
    screen: SurfaceLike,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int = DEFAULT_FONT_SIZE,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    # Calculate position for right alignment
    width, _ = font.size(str(text))
    _blit_surface(screen, text_surf, (x - width, y))


def message_display_MB(
    screen: SurfaceLike,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int = DEFAULT_FONT_SIZE,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    # Calculate position for middle bottom alignment
    width, height = font.size(str(text))
    _blit_surface(screen, text_surf, (x - width // 2, y - height))


def message_display_MT(
    screen: SurfaceLike,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    # Calculate position for middle top alignment
    width, _ = font.size(str(text))
    _blit_surface(screen, text_surf, (x - width // 2, y))


def message_display(
    screen: SurfaceLike,
    text: str,
    x: Coordinate,
    y: Coordinate,
    size: int,
    color: ColorValue = colors.WHITE,
) -> None:
    font = _get_font(size)
    text_surf, text_rect = text_object(text, font, color)
    # Calculate position for center alignment
    width, height = font.size(str(text))
    _blit_surface(screen, text_surf, (x - width // 2, y - height // 2))


def truncline(text: str, maxwidth: int, font: "Font") -> tuple[int, int, str]:
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
        backend = get_backend()
        font = backend.graphics.load_font(FONT_PATH, size)
    while not done:
        nl, done, stext = truncline(text, pixel_max_width, font)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped
