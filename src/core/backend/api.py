"""
Backend API interfaces for graphics, input, and audio abstractions.

This module defines the abstract interfaces that backend implementations must provide,
allowing the rest of the application to remain independent of pygame or other backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from core.colors import ColorValue, Coordinate

# Event type constants (pygame values - will be overridden by backend implementation if different)
QUIT: int = 256  # pygame.QUIT
KEYDOWN: int = 768  # pygame.KEYDOWN
KEYUP: int = 769  # pygame.KEYUP
MOUSEBUTTONDOWN: int = 1025  # pygame.MOUSEBUTTONDOWN
MOUSEBUTTONUP: int = 1026  # pygame.MOUSEBUTTONUP
MOUSEMOTION: int = 1024  # pygame.MOUSEMOTION

# Key constants (will be overridden by backend implementation)
K_1: int = 49
K_2: int = 50
K_3: int = 51
K_4: int = 52
K_5: int = 53
K_LEFT: int = 1073741904
K_RIGHT: int = 1073741903
K_UP: int = 1073741906
K_DOWN: int = 1073741905
K_RETURN: int = 13
K_SPACE: int = 32
K_ESCAPE: int = 27
K_p: int = 112
K_q: int = 113
K_w: int = 119
K_a: int = 97
K_s: int = 115
K_d: int = 100
K_b: int = 98
K_c: int = 99
K_f: int = 102
K_g: int = 103
K_v: int = 118
K_x: int = 120
K_z: int = 122

# Event types
class Event:
    """Base event class for backend-agnostic events."""
    def __init__(self, type: int, **kwargs):
        self.type = type
        self.key: int | None = None  # Key code for keyboard events
        for key, value in kwargs.items():
            setattr(self, key, value)

# Graphics surface interface
class GraphicsSurface(ABC):
    """Abstract interface for graphics surfaces and drawing operations."""
    
    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        """Get the width and height of the surface."""
        pass

    def get_width(self) -> int:
        """Get the width of the surface."""
        return self.get_size()[0]

    def get_height(self) -> int:
        """Get the height of the surface."""
        return self.get_size()[1]

    @abstractmethod
    def blit(self, source: GraphicsSurface, dest: tuple[Coordinate, Coordinate] | Coordinate):
        """Draw the source surface onto this surface at the destination."""
        pass

    @abstractmethod
    def fill(self, color: ColorValue) -> None:
        """Fill the entire surface with the given color."""
        pass

    @abstractmethod
    def convert(self) -> GraphicsSurface:
        """Optimize the surface for display."""
        pass

    @abstractmethod
    def set_alpha(self, alpha: int | None) -> None:
        """Set the alpha value for the surface."""
        pass

    @abstractmethod
    def set_colorkey(self, color: ColorValue | None) -> None:
        """Set the color key for transparency."""
        pass


class Font(ABC):
    """Abstract interface for font rendering."""
    
    @abstractmethod
    def render(self, text: str, antialias: bool, color: ColorValue) -> GraphicsSurface:
        """Render text to a surface."""
        pass

    @abstractmethod
    def size(self, text: str) -> tuple[int, int]:
        """Get the dimensions of the rendered text."""
        pass


class Texture(ABC):
    """Abstract interface for textures/images."""
    
    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        """Get the width and height of the texture."""
        pass


class GraphicsBackend(ABC):
    """Main graphics backend interface."""
    
    @abstractmethod
    def create_surface(self, size: tuple[int, int]) -> GraphicsSurface:
        """Create a new surface with the given size."""
        pass

    @abstractmethod
    def load_texture(self, filepath: str) -> Texture:
        """Load a texture from a file."""
        pass

    @abstractmethod
    def load_image(self, filepath: str) -> GraphicsSurface:
        """Load an image from a file as a GraphicsSurface."""
        pass

    @abstractmethod
    def load_font(self, filepath: str, size: int) -> Font:
        """Load a font from a file with the given size."""
        pass

    @abstractmethod
    def get_display_surface(self) -> GraphicsSurface:
        """Get the main display surface."""
        pass

    @abstractmethod
    def set_display_mode(self, size: tuple[int, int], flags: int = 0) -> GraphicsSurface:
        """Set the display mode and return the surface."""
        pass

    @abstractmethod
    def set_caption(self, caption: str) -> None:
        """Set the window title."""
        pass

    @abstractmethod
    def set_icon(self, icon: Texture) -> None:
        """Set the window icon."""
        pass

    @abstractmethod
    def draw_rect(self, surface: GraphicsSurface, color: ColorValue, rect: tuple[Coordinate, Coordinate, Coordinate, Coordinate]):
        """Draw a rectangle on the surface."""
        pass

    @abstractmethod
    def draw_circle(self, surface: GraphicsSurface, color: ColorValue, center: tuple[Coordinate, Coordinate], radius: int):
        """Draw a circle on the surface."""
        pass

    @abstractmethod
    def draw_line(self, surface: GraphicsSurface, color: ColorValue, start_pos: tuple[Coordinate, Coordinate], end_pos: tuple[Coordinate, Coordinate], width: int = 1):
        """Draw a line on the surface."""
        pass

    @abstractmethod
    def draw_polygon(self, surface: GraphicsSurface, color: ColorValue, points: list[tuple[Coordinate, Coordinate]]):
        """Draw a polygon on the surface."""
        pass

    @abstractmethod
    def scale_surface(self, surface: GraphicsSurface, size: tuple[int, int]) -> GraphicsSurface:
        """Scale a surface to a new size."""
        pass

    @abstractmethod
    def flip_surface(self, surface: GraphicsSurface, flip_x: bool, flip_y: bool) -> GraphicsSurface:
        """Flip a surface horizontally and/or vertically."""
        pass

    @abstractmethod
    def flip(self) -> None:
        """Update the display with the current surface."""
        pass


class InputBackend(ABC):
    """Input backend interface for handling events and input states."""
    
    @abstractmethod
    def get_events(self) -> list[Event]:
        """Get all pending events."""
        pass

    @abstractmethod
    def get_pressed_keys(self) -> Sequence[bool]:
        """Get the current state of all keyboard keys."""
        pass

    @abstractmethod
    def get_mouse_pos(self) -> tuple[int, int]:
        """Get the current mouse position."""
        pass

    @abstractmethod
    def get_mouse_rel(self) -> tuple[int, int]:
        """Get the relative mouse movement since the last call."""
        pass

    @abstractmethod
    def get_mouse_pressed(self) -> tuple[bool, bool, bool]:
        """Get the current state of mouse buttons (left, middle, right)."""
        pass

    @abstractmethod
    def set_mouse_pos(self, pos: tuple[int, int]) -> None:
        """Set the mouse position."""
        pass

    @abstractmethod
    def set_mouse_visible(self, visible: bool) -> None:
        """Set whether the mouse cursor is visible."""
        pass

    @abstractmethod
    def set_event_grab(self, grabbed: bool) -> None:
        """Set whether the application should grab all input events."""
        pass

    @abstractmethod
    def set_allowed_events(self, event_types: list[str]) -> None:
        """Set which event types are allowed."""
        pass


class Sound(ABC):
    """Abstract interface for audio sounds."""
    
    @abstractmethod
    def play(self, loops: int = 0, maxtime: int = 0, fade_ms: int = 0) -> Channel | None:
        """Play the sound."""
        pass


class Channel(ABC):
    """Abstract interface for audio channels."""
    
    @abstractmethod
    def play(self, sound: Sound, loops: int = 0, maxtime: int = 0, fade_ms: int = 0) -> None:
        """Play a sound on this channel."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop playing on this channel."""
        pass

    @abstractmethod
    def get_busy(self) -> bool:
        """Check if this channel is currently playing."""
        pass

    @abstractmethod
    def set_volume(self, left: float, right: float) -> None:
        """Set the volume on this channel."""
        pass


class AudioBackend(ABC):
    """Audio backend interface."""
    
    @abstractmethod
    def init(self, frequency: int = 44100, size: int = -16, channels: int = 2, buffer: int = 512) -> bool:
        """Initialize the audio system."""
        pass

    @abstractmethod
    def load_sound(self, filepath: str) -> Sound:
        """Load a sound file."""
        pass

    @abstractmethod
    def get_init(self) -> bool:
        """Check if the audio system is initialized."""
        pass

    @abstractmethod
    def find_channel(self, force: bool = False) -> Channel | None:
        """Find an available audio channel."""
        pass

    @abstractmethod
    def pre_init(self, frequency: int, size: int, channels: int, buffer: int) -> None:
        """Pre-initialize the audio system."""
        pass


class Clock(ABC):
    """Abstract interface for timing and frame rate control."""
    
    @abstractmethod
    def tick(self, framerate: int = 0) -> int:
        """Control the frame rate and return the time since the last call."""
        pass

    @abstractmethod
    def get_time(self) -> int:
        """Get the time in milliseconds since the last tick."""
        pass

    @abstractmethod
    def get_fps(self) -> float:
        """Get the current average frames per second."""
        pass


class Backend(ABC):
    """Main backend interface that combines all subsystems."""
    
    @property
    @abstractmethod
    def graphics(self) -> GraphicsBackend:
        """The graphics backend instance."""
        pass

    @property
    @abstractmethod
    def input(self) -> InputBackend:
        """The input backend instance."""
        pass

    @property
    @abstractmethod
    def audio(self) -> AudioBackend:
        """The audio backend instance."""
        pass

    @property
    @abstractmethod
    def clock(self) -> Clock:
        """The clock backend instance."""
        pass

    @abstractmethod
    def init(self) -> bool:
        """Initialize the backend."""
        pass

    @abstractmethod
    def quit(self) -> None:
        """Clean up and quit the backend."""
        pass