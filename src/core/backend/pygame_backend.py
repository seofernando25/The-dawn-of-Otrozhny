"""
Pygame backend implementation for the game backend abstraction.

This module provides concrete implementations of the backend interfaces
using pygame as the underlying library.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from collections.abc import Sequence

if TYPE_CHECKING:
    from core.backend.api import ColorValue, Coordinate

import pygame
import pygame.mixer
from core.backend.api import (
    AudioBackend,
    Backend,
    Channel,
    Clock,
    Event,
    Font,
    GraphicsBackend,
    GraphicsSurface,
    InputBackend,
    Sound,
    Texture,
)


class PygameGraphicsSurface(GraphicsSurface):
    """Pygame implementation of GraphicsSurface."""
    
    def __init__(self, surface: pygame.Surface):
        self._surface = surface

    def get_size(self) -> tuple[int, int]:
        return self._surface.get_size()

    def blit(self, source: GraphicsSurface, dest: tuple[Coordinate, Coordinate] | Coordinate):
        # Normalize dest to always be a tuple (pygame requires tuple, not single Coordinate)
        if isinstance(dest, (int, float)):
            dest_tuple: tuple[Coordinate, Coordinate] = (dest, dest)
        else:
            dest_tuple = dest
        
        if isinstance(source, PygameGraphicsSurface):
            _ = self._surface.blit(source._surface, dest_tuple)
        elif isinstance(source, pygame.Surface):
            # Allow direct pygame.Surface for backward compatibility
            _ = self._surface.blit(source, dest_tuple)
        else:
            raise TypeError(f"Expected PygameGraphicsSurface or pygame.Surface, got {type(source)}")

    def fill(self, color: ColorValue):
        self._surface.fill(color)

    def convert(self) -> GraphicsSurface:
        converted_surface = self._surface.convert()
        return PygameGraphicsSurface(converted_surface)

    def set_alpha(self, alpha: int | None):
        self._surface.set_alpha(alpha)

    def set_colorkey(self, color: ColorValue | None):
        self._surface.set_colorkey(color)


class PygameFont(Font):
    """Pygame implementation of Font."""
    
    def __init__(self, font: pygame.font.Font):
        self._font = font

    def render(self, text: str, antialias: bool, color: ColorValue):
        rendered_surface = self._font.render(str(text), antialias, color)
        return PygameGraphicsSurface(rendered_surface)

    def size(self, text: str) -> tuple[int, int]:
        return self._font.size(str(text))


class PygameTexture(Texture):
    """Pygame implementation of Texture."""
    
    def __init__(self, surface: pygame.Surface):
        self._surface = surface

    def get_size(self) -> tuple[int, int]:
        return self._surface.get_size()


class PygameGraphicsBackend(GraphicsBackend):
    """Pygame implementation of GraphicsBackend."""
    
    def create_surface(self, size: tuple[int, int]) -> GraphicsSurface:
        surface = pygame.Surface(size)
        return PygameGraphicsSurface(surface)

    def load_texture(self, filepath: str) -> Texture:
        surface = pygame.image.load(filepath)
        # Use convert_alpha if display is initialized, otherwise return as-is
        # (caller should ensure display is initialized before loading textures)
        if pygame.display.get_surface() is not None:
            surface = surface.convert_alpha()
        return PygameTexture(surface)

    def load_image(self, filepath: str) -> GraphicsSurface:
        """Load an image from a file as a GraphicsSurface."""
        surface = pygame.image.load(filepath)
        # Use convert_alpha if display is initialized, otherwise return as-is
        if pygame.display.get_surface() is not None:
            surface = surface.convert_alpha()
        return PygameGraphicsSurface(surface)

    def load_font(self, filepath: str, size: int) -> Font:
        font = pygame.font.Font(filepath, size)
        return PygameFont(font)

    def get_display_surface(self) -> GraphicsSurface:
        surface = pygame.display.get_surface()
        if surface is None:
            raise RuntimeError("No display surface available")
        return PygameGraphicsSurface(surface)

    def set_display_mode(self, size: tuple[int, int], flags: int = 0) -> GraphicsSurface:
        # Use default pygame flags if none specified
        if flags == 0:
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        surface = pygame.display.set_mode(size, flags)
        return PygameGraphicsSurface(surface)

    def set_caption(self, caption: str) -> None:
        pygame.display.set_caption(caption)

    def set_icon(self, icon: Texture) -> None:
        if isinstance(icon, PygameTexture):
            pygame.display.set_icon(icon._surface)
        else:
            raise TypeError(f"Expected PygameTexture, got {type(icon)}")

    def _resolve_surface(self, surface: GraphicsSurface) -> pygame.Surface:
        if isinstance(surface, PygameGraphicsSurface):
            return surface._surface
        if isinstance(surface, pygame.Surface):
            return surface
        raise TypeError(f"Expected GraphicsSurface or pygame.Surface, got {type(surface)}")

    def draw_rect(self, surface: GraphicsSurface, color: ColorValue, rect: tuple[Coordinate, Coordinate, Coordinate, Coordinate]):
        target = self._resolve_surface(surface)
        _ = pygame.draw.rect(target, color, rect)

    def draw_circle(self, surface: GraphicsSurface, color: ColorValue, center: tuple[Coordinate, Coordinate], radius: int):
        target = self._resolve_surface(surface)
        _ = pygame.draw.circle(target, color, center, radius)

    def draw_line(self, surface: GraphicsSurface, color: ColorValue, start_pos: tuple[Coordinate, Coordinate], end_pos: tuple[Coordinate, Coordinate], width: int = 1):
        target = self._resolve_surface(surface)
        _ = pygame.draw.line(target, color, start_pos, end_pos, width)

    def draw_polygon(self, surface: GraphicsSurface, color: ColorValue, points: list[tuple[Coordinate, Coordinate]]):
        target = self._resolve_surface(surface)
        _ = pygame.draw.polygon(target, color, points)

    def scale_surface(self, surface: GraphicsSurface, size: tuple[int, int]) -> GraphicsSurface:
        target = self._resolve_surface(surface)
        scaled = pygame.transform.scale(target, size)
        return PygameGraphicsSurface(scaled)

    def flip_surface(self, surface: GraphicsSurface, flip_x: bool, flip_y: bool) -> GraphicsSurface:
        target = self._resolve_surface(surface)
        flipped = pygame.transform.flip(target, flip_x, flip_y)
        return PygameGraphicsSurface(flipped)

    def flip(self) -> None:
        pygame.display.flip()


class PygameInputBackend(InputBackend):
    """Pygame implementation of InputBackend."""
    
    def get_events(self) -> list[Event]:
        pygame_events = pygame.event.get()
        events = []
        for event in pygame_events:
            # Convert pygame event to our abstract event
            # Keep the pygame event type constant for compatibility
            event_obj = Event(type=event.type)
            # Copy all non-callable attributes from pygame event
            for attr_name in dir(event):
                if attr_name.startswith('_'):
                    continue
                try:
                    attr_value = getattr(event, attr_name)
                    # Skip callable attributes and methods
                    if callable(attr_value):
                        continue
                    # Copy the attribute value (including None for some attributes)
                    # But for 'key', we want to copy it even if it's None for non-keyboard events
                    setattr(event_obj, attr_name, attr_value)
                except (AttributeError, TypeError):
                    pass
            events.append(event_obj)
        return events

    def get_pressed_keys(self) -> Sequence[bool]:
        return pygame.key.get_pressed()

    def get_mouse_pos(self) -> tuple[int, int]:
        return pygame.mouse.get_pos()

    def get_mouse_rel(self) -> tuple[int, int]:
        return pygame.mouse.get_rel()

    def get_mouse_pressed(self) -> tuple[bool, bool, bool]:
        return pygame.mouse.get_pressed()

    def set_mouse_pos(self, pos: tuple[int, int]) -> None:
        pygame.mouse.set_pos(pos)

    def set_mouse_visible(self, visible: bool) -> None:
        pygame.mouse.set_visible(visible)

    def set_event_grab(self, grabbed: bool) -> None:
        pygame.event.set_grab(grabbed)

    def set_allowed_events(self, event_types: list[str]) -> None:
        # Map string event names to pygame constants
        event_map = {
            "QUIT": pygame.QUIT,
            "KEYDOWN": pygame.KEYDOWN,
            "KEYUP": pygame.KEYUP,
            "MOUSEBUTTONDOWN": pygame.MOUSEBUTTONDOWN,
            "MOUSEBUTTONUP": pygame.MOUSEBUTTONUP,
            "MOUSEMOTION": pygame.MOUSEMOTION,
            "MOUSEWHEEL": pygame.MOUSEWHEEL,
            "VIDEORESIZE": pygame.VIDEORESIZE,
            "VIDEOEXPOSE": pygame.VIDEOEXPOSE,
            "USEREVENT": pygame.USEREVENT,
        }

        event_constants = []
        for event_type in event_types:
            if event_type in event_map:
                event_constants.append(event_map[event_type])
            else:
                # If not in our map, assume it's already a pygame constant (for flexibility)
                # This shouldn't happen in our codebase since we control the event names
                pass

        pygame.event.set_allowed(event_constants)


class PygameSound(Sound):
    """Pygame implementation of Sound."""
    
    def __init__(self, sound: pygame.mixer.Sound):
        self._sound = sound

    def play(self, loops: int = 0, maxtime: int = 0, fade_ms: int = 0):
        channel = self._sound.play(loops, maxtime, fade_ms)
        return PygameChannel(channel)


class PygameChannel(Channel):
    """Pygame implementation of Channel."""
    
    def __init__(self, channel: pygame.mixer.Channel):
        self._channel = channel

    def play(self, sound: Sound, loops: int = 0, maxtime: int = 0, fade_ms: int = 0) -> None:
        if isinstance(sound, PygameSound):
            self._channel.play(sound._sound, loops, maxtime, fade_ms)
        else:
            raise TypeError(f"Expected PygameSound, got {type(sound)}")

    def stop(self) -> None:
        self._channel.stop()

    def get_busy(self) -> bool:
        return self._channel.get_busy()

    def set_volume(self, left: float, right: float) -> None:
        self._channel.set_volume(left, right)


class PygameAudioBackend(AudioBackend):
    """Pygame implementation of AudioBackend."""
    
    def init(self, frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 512) -> bool:
        try:
            pygame.mixer.pre_init(frequency, size, channels, buffer)
            pygame.mixer.init()
            return True
        except pygame.error:
            return False

    def load_sound(self, filepath: str) -> Sound:
        sound = pygame.mixer.Sound(filepath)
        return PygameSound(sound)

    def get_init(self) -> bool:
        return bool(pygame.mixer.get_init())

    def find_channel(self, force: bool = False) -> Channel | None:
        channel = pygame.mixer.find_channel(force)
        return PygameChannel(channel)

    def pre_init(self, frequency: int, size: int, channels: int, buffer: int) -> None:
        pygame.mixer.pre_init(frequency, size, channels, buffer)


class PygameClock(Clock):
    """Pygame implementation of Clock."""
    
    def __init__(self):
        self._clock = pygame.time.Clock()

    def tick(self, framerate: int = 0) -> int:
        return self._clock.tick(framerate)

    def get_time(self) -> int:
        return self._clock.get_time()

    def get_fps(self) -> float:
        return self._clock.get_fps()


# Define pygame constants at module level to ensure they're available after pygame import
QUIT = pygame.QUIT
KEYDOWN = pygame.KEYDOWN
KEYUP = pygame.KEYUP
MOUSEBUTTONDOWN = pygame.MOUSEBUTTONDOWN
MOUSEBUTTONUP = pygame.MOUSEBUTTONUP
MOUSEMOTION = pygame.MOUSEMOTION
MOUSEWHEEL = pygame.MOUSEWHEEL
VIDEORESIZE = pygame.VIDEORESIZE
VIDEOEXPOSE = pygame.VIDEOEXPOSE
USEREVENT = pygame.USEREVENT

# Key constants
K_p = pygame.K_p


class PygameBackend(Backend):
    """Complete Pygame backend implementation."""

    def __init__(self):
        self._graphics = PygameGraphicsBackend()
        self._input = PygameInputBackend()
        self._audio = PygameAudioBackend()
        self._clock = PygameClock()

    @property
    def graphics(self):
        return self._graphics

    @property
    def input(self):
        return self._input

    @property
    def audio(self):
        return self._audio

    @property
    def clock(self):
        return self._clock

    def init(self) -> bool:
        pygame.init()
        # Update the api module constants to reflect the actual pygame values
        import core.backend.api as api
        api.QUIT = QUIT
        api.KEYDOWN = KEYDOWN
        api.KEYUP = KEYUP
        api.MOUSEBUTTONDOWN = MOUSEBUTTONDOWN
        api.MOUSEBUTTONUP = MOUSEBUTTONUP
        api.MOUSEMOTION = MOUSEMOTION
        api.K_p = K_p
        return True

    def quit(self) -> None:
        pygame.quit()