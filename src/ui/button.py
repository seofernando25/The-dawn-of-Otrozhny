"""HUD button component."""
import pygame
import rendering as renderer
import colors
from renderer.text import message_display, message_display_MT, wrapline


class HudButton(pygame.Surface):
    """A button component for the HUD system."""
    
    activated_sound = None

    def __init__(self, w, h, text="None"):
        super().__init__((w, h))
        self.isActive = False
        # If false the surface have to be redrawn step by step
        self.protected = True
        self.text = str(text)
        self.subtitle = ""
        self.title = ""
        self.indexColor = [colors.WHITE] * 3
        self._dirty = True

    def _mark_dirty(self):
        """Mark the button as needing a redraw."""
        if self.protected:
            self._dirty = True

    def set_color(self, textIndex, color):
        """Set the color for a specific text element."""
        if self.indexColor[textIndex] != color:
            self.indexColor[textIndex] = color
            self._mark_dirty()

    def set_subtitle(self, text):
        """Set the subtitle text."""
        text = "" if text is None else str(text)
        if text != self.subtitle:
            self.subtitle = text
            self._mark_dirty()

    def set_title(self, text):
        """Set the title text."""
        text = "" if text is None else str(text)
        if text != self.title:
            self.title = text
            self._mark_dirty()

    def set_text(self, text):
        """Set the main text."""
        text = "" if text is None else str(text)
        if text != self.text:
            self.text = text
            self._mark_dirty()

    def _render_contents(self):
        """Render the button's text contents."""
        if self.title:
            message_display_MT(
                self,
                self.title,
                self.get_width() // 2,
                renderer.HUD_CELL_TITLE_OFFSET,
                renderer.HUD_CELL_TITLE_FONT_SIZE,
                self.indexColor[0],
            )
        if self.subtitle:
            message_display_MT(
                self,
                self.subtitle,
                self.get_width() // 2,
                renderer.HUD_CELL_TITLE_OFFSET * 3,
                renderer.HUD_CELL_TITLE_FONT_SIZE,
                self.indexColor[1],
            )

        if self.text:
            wrapped_text = wrapline(
                self.text, self.get_width(), renderer.HUD_CELL_TITLE_FONT_SIZE
            )
            py = self.get_height() // 2
            if self.subtitle:
                py += renderer.HUD_CELL_TITLE_OFFSET
            if len(wrapped_text) > 1:
                py -= (len(wrapped_text) // 2) * renderer.HUD_CELL_TITLE_FONT_SIZE

            for line in wrapped_text:
                message_display(
                    self,
                    line,
                    self.get_width() // 2,
                    py,
                    renderer.HUD_CELL_TITLE_FONT_SIZE,
                    self.indexColor[2],
                )
                py += renderer.HUD_CELL_TITLE_FONT_SIZE + renderer.HUD_CELL_OFFSET

    def redraw(self):
        """Redraw the button if it's marked as dirty."""
        if not self.protected or not self._dirty:
            return
        self.fill(self.get_color())
        self._render_contents()
        self._dirty = False

    def get_color(self):
        """Get the background color based on active state."""
        if self.isActive:
            return colors.GRAY_VARIATION_1
        elif not self.isActive:
            return colors.GRAY_VARIATION_3

    def set_active(self, active):
        """Set the active state of the button."""
        if self.isActive == active:
            return
        self.isActive = active
        if active and HudButton.activated_sound is not None:
            HudButton.activated_sound.play()
        self._mark_dirty()
        self.redraw()

