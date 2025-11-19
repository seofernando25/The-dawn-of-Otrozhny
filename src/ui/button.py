"""HUD button component."""

import pygame

from config import renderer_config
from core import colors
from renderer.text import message_display, message_display_MT, wrapline

ColorValue = tuple[int, int, int] | list[int] | str


class HudButton(pygame.Surface):
    """A button component for the HUD system."""

    def __init__(
        self,
        w: float,
        h: float,
        text: str = "None",
        *,
        activated_sound: pygame.mixer.Sound | None = None,
    ):
        super().__init__((int(w), int(h)))
        self.isActive: bool = False
        # If false the surface have to be redrawn step by step
        self.protected: bool = True
        self.text: str = str(text)
        self.subtitle: str = ""
        self.title: str = ""
        self.indexColor: list[ColorValue] = [colors.WHITE] * 3
        self._dirty: bool = True
        self._activated_sound: pygame.mixer.Sound | None = activated_sound

    def _mark_dirty(self):
        """Mark the button as needing a redraw."""
        if self.protected:
            self._dirty = True

    def set_color(self, textIndex: int, color: ColorValue) -> None:
        """Set the color for a specific text element."""
        if self.indexColor[textIndex] != color:
            self.indexColor[textIndex] = color
            self._mark_dirty()

    def set_subtitle(self, text: str | None) -> None:
        """Set the subtitle text."""
        text = "" if text is None else str(text)
        if text != self.subtitle:
            self.subtitle = text
            self._mark_dirty()

    def set_title(self, text: str | None) -> None:
        """Set the title text."""
        text = "" if text is None else str(text)
        if text != self.title:
            self.title = text
            self._mark_dirty()

    def set_text(self, text: str | None) -> None:
        """Set the main text."""
        text = "" if text is None else str(text)
        if text != self.text:
            self.text = text
            self._mark_dirty()

    def _render_contents(self) -> None:
        """Render the button's text contents."""
        if self.title:
            message_display_MT(
                self,
                self.title,
                self.get_width() // 2,
                renderer_config.HUD_CELL_TITLE_OFFSET,
                renderer_config.HUD_CELL_TITLE_FONT_SIZE,
                self.indexColor[0],
            )
        if self.subtitle:
            message_display_MT(
                self,
                self.subtitle,
                self.get_width() // 2,
                renderer_config.HUD_CELL_TITLE_OFFSET * 3,
                renderer_config.HUD_CELL_TITLE_FONT_SIZE,
                self.indexColor[1],
            )

        if self.text:
            wrapped_text = wrapline(
                self.text, self.get_width(), renderer_config.HUD_CELL_TITLE_FONT_SIZE
            )
            py = self.get_height() // 2
            if self.subtitle:
                py += renderer_config.HUD_CELL_TITLE_OFFSET
            if len(wrapped_text) > 1:
                py -= (
                    len(wrapped_text) // 2
                ) * renderer_config.HUD_CELL_TITLE_FONT_SIZE

            for line in wrapped_text:
                message_display(
                    self,
                    line,
                    self.get_width() // 2,
                    py,
                    renderer_config.HUD_CELL_TITLE_FONT_SIZE,
                    self.indexColor[2],
                )
                py += (
                    renderer_config.HUD_CELL_TITLE_FONT_SIZE
                    + renderer_config.HUD_CELL_OFFSET
                )

    def redraw(self) -> None:
        """Redraw the button if it's marked as dirty."""
        if not self.protected or not self._dirty:
            return
        _ = self.fill(self.get_color())
        self._render_contents()
        self._dirty = False

    def get_color(self) -> tuple[int, int, int]:
        """Get the background color based on active state."""
        if self.isActive:
            return colors.GRAY_VARIATION_1
        else:
            return colors.GRAY_VARIATION_3

    def set_active(self, active: bool) -> None:
        """Set the active state of the button."""
        if self.isActive == active:
            return
        self.isActive = active
        if active and self._activated_sound is not None:
            _ = self._activated_sound.play()
        self._mark_dirty()
        self.redraw()
