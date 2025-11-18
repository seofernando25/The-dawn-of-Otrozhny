# Classes that wrap around ui elements
# as a layer of abstraction to increase productivity
from typing import List

import rendering as renderer
import mathHelpers
import colors
import pygame.constants as pyConst
import pygame
import textDraw
import textHelpers


class HudScreen():

    def __init__(self, interactable=True, dynamic=False):
        self.viewPort = _generate_hud_viewport()
        self.viewPort.fill(colors.GRAY_VARIATION_2)
        self.hud_buttons = _generate_hud_surfaces(self.viewPort)
        self.interactable = interactable
        self.dynamic = dynamic
        self.selected_button = 0
        self.cursorX = self.selected_button
        # Should have created an event handler class :/
        self.onChangedButton = []

    def set_button_color(self, buttonIndex, textIndex, color):
        self.hud_buttons[buttonIndex].set_color(textIndex, color)

    def set_button_subtitle(self, buttonIndex, text):
        self.hud_buttons[buttonIndex].set_subtitle(text)

    def set_button_title(self, buttonIndex, text):
        self.hud_buttons[buttonIndex].set_title(text)

    def set_button_text(self, buttonIndex, text):
        self.hud_buttons[buttonIndex].set_text(text)

    def draw(self):
        if self.interactable or self.dynamic:
            self.viewPort.fill(colors.GRAY_VARIATION_2)
        render_hud_surfaces(self.viewPort, self.hud_buttons)

        if self.interactable:
            pygame.draw.rect(self.viewPort, colors.BLACK, [int(
                self.cursorX * (self.viewPort.get_width()/5) + renderer.HUD_CELL_OFFSET + 5), self.viewPort.get_height(), 100, -10])
        screen = renderer.get_screen()
        screen.blit(self.viewPort, (renderer.VIEWPORT_X_OFFSET,
                                    renderer.SCREEN_HEIGHT - self.viewPort.get_height() - renderer.VIEWPORT_Y_OFFSET//4))

    def change_selected_button(self, amount, change_to=False):
        for x in self.onChangedButton:
            x()

        self.hud_buttons[self.selected_button].set_active(False)
        self.selected_button += amount
        if change_to:
            self.selected_button = amount
        if self.selected_button < 0:
            self.selected_button = renderer.HUD_NUM_OF_CELLS - 1
        elif self.selected_button > renderer.HUD_NUM_OF_CELLS - 1:
            self.selected_button = 0
        self.hud_buttons[self.selected_button].set_active(True)

    def update(self, dt, events):
        if self.interactable:
            self.cursorX = mathHelpers.lerp(
                self.cursorX, self.selected_button, dt * 15)
            for event in events:
                if event.type == pygame.KEYDOWN:

                    if event.key == pyConst.K_LEFT:
                        self.change_selected_button(-1)

                    if event.key == pyConst.K_RIGHT:
                        self.change_selected_button(1)

                    if event.key == pyConst.K_1:
                        self.change_selected_button(0, True)

                    if event.key == pyConst.K_2:
                        self.change_selected_button(1, True)

                    if event.key == pyConst.K_3:
                        self.change_selected_button(2, True)

                    if event.key == pyConst.K_4:
                        self.change_selected_button(3, True)

                    if event.key == pyConst.K_5:
                        self.change_selected_button(4, True)

                    if event.key == pyConst.K_RETURN or event.key == pyConst.K_SPACE:
                        return self.selected_button


class VerticalList():
    def __init__(self, str_list, px, py):
        self.items = str_list
        self.objects = []
        self.px = px
        self.py = py
        font = pygame.font.Font(
            textDraw.FONT_PATH, renderer.HUD_CELL_TITLE_FONT_SIZE)
        for line in str_list:
            self.objects.append(
                HudButton(font.size(line)[0], renderer.HUD_CELL_TITLE_FONT_SIZE, line))

    def draw(self):
        for buttons in self.objects:
            buttons.redraw()
        screen = renderer.get_screen()
        for x in range(len(self.objects)):
            screen.blit(
                self.objects[x], (self.px, self.py + x * renderer.HUD_CELL_TITLE_FONT_SIZE + x * 10))


def render_hud_surfaces(hud_viewport, hud_cell_surfaces):
    row = 0
    for cell_surface in hud_cell_surfaces:
        cell_surface.redraw()
        hud_viewport.blit(cell_surface, (renderer.HUD_CELL_OFFSET + renderer.HUD_CELL_OFFSET * row + row * cell_surface.get_width(),
                                         renderer.VIEWPORT_Y_OFFSET//4))
        row += 1

# 3 by 5


class MapSelectionScreen(pygame.Surface):
    def __init__(self):
        pygame.Surface.__init__(
            self, (renderer.SCREEN_WIDTH, renderer.SCREEN_HEIGHT))
        self.hud_buttons: List[List[HudButton]] = [
            [HudButton(100, 100, text=str((x, y))) for y in range(3)]
            for x in range(5)
        ]
        self.selected_button_x = 0
        self.selected_button_y = 0
        self._pointer_x = 100
        self._pointer_y = 150
        for column in self.hud_buttons:
            for button in column:
                button.redraw()
                button.protected = False

    def draw(self):
        self.fill(colors.BLACK)
        for x in range(5):
            for y in range(3):
                self.blit(
                    self.hud_buttons[x][y], (50 + x*100 + x * renderer.HUD_CELL_OFFSET,
                                             100 + y*100 + y*renderer.HUD_CELL_OFFSET)
                )

        pygame.draw.circle(self, colors.WHITE, (int(
            self._pointer_x), int(self._pointer_y)), 10)
        renderer.get_screen().blit(self, (0, 0))

    def update(self, dt, events):
        pos = (100 + self.selected_button_x*100 + self.selected_button_x * renderer.HUD_CELL_OFFSET,
               150 + self.selected_button_y*100 + self.selected_button_y*renderer.HUD_CELL_OFFSET)
        self._pointer_x = mathHelpers.lerp(self._pointer_x, pos[0], dt * 10)
        self._pointer_y = mathHelpers.lerp(self._pointer_y, pos[1], dt * 10)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.change_selected_button(-1)
                elif event.key == pygame.K_RIGHT:
                    self.change_selected_button(1)
                elif event.key == pygame.K_UP:
                    self.change_selected_button(-1, False)
                elif event.key == pygame.K_DOWN:
                    self.change_selected_button(1, False)
        self.draw()

    def change_selected_button(self, amount, change_x=True):
        self.hud_buttons[self.selected_button_x][self.selected_button_y].set_active(
            False)
        if change_x:
            self.selected_button_x += amount
            if self.selected_button_x < 0:
                self.change_selected_button(-1, False)
                self.selected_button_x = 4
            elif self.selected_button_x > 4:
                self.selected_button_x = 0
                self.change_selected_button(1, False)
        else:
            self.selected_button_y += amount
            if self.selected_button_y < 0:
                self.selected_button_y = 2
            elif self.selected_button_y > 2:
                self.selected_button_y = 0
        self.hud_buttons[self.selected_button_x][self.selected_button_y].set_active(
            True)


class HudButton(pygame.Surface):
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
        if self.protected:
            self._dirty = True

    def set_color(self, textIndex, color):
        if self.indexColor[textIndex] != color:
            self.indexColor[textIndex] = color
            self._mark_dirty()

    def set_subtitle(self, text):
        text = "" if text is None else str(text)
        if text != self.subtitle:
            self.subtitle = text
            self._mark_dirty()

    def set_title(self, text):
        text = "" if text is None else str(text)
        if text != self.title:
            self.title = text
            self._mark_dirty()

    def set_text(self, text):
        text = "" if text is None else str(text)
        if text != self.text:
            self.text = text
            self._mark_dirty()

    def _render_contents(self):
        if self.title:
            textDraw.message_display_MT(
                self, self.title,
                self.get_width()//2, renderer.HUD_CELL_TITLE_OFFSET,
                renderer.HUD_CELL_TITLE_FONT_SIZE, self.indexColor[0])
        if self.subtitle:
            textDraw.message_display_MT(
                self, self.subtitle,
                self.get_width()//2, renderer.HUD_CELL_TITLE_OFFSET * 3,
                renderer.HUD_CELL_TITLE_FONT_SIZE, self.indexColor[1])

        if self.text:
            wrapped_text = textHelpers.wrapline(
                self.text, self.get_width(), renderer.HUD_CELL_TITLE_FONT_SIZE)
            py = self.get_height()//2
            if self.subtitle:
                py += renderer.HUD_CELL_TITLE_OFFSET
            if len(wrapped_text) > 1:
                py -= (len(wrapped_text)//2) * renderer.HUD_CELL_TITLE_FONT_SIZE

            for line in wrapped_text:
                textDraw.message_display(
                    self, line, self.get_width()//2, py,
                    renderer.HUD_CELL_TITLE_FONT_SIZE, self.indexColor[2])
                py += renderer.HUD_CELL_TITLE_FONT_SIZE + renderer.HUD_CELL_OFFSET

    def redraw(self):
        if not self.protected or not self._dirty:
            return
        self.fill(self.get_color())
        self._render_contents()
        self._dirty = False

    def get_color(self):
        if self.isActive:
            return colors.GRAY_VARIATION_1
        elif not self.isActive:
            return colors.GRAY_VARIATION_3

    def set_active(self, active):
        if self.isActive == active:
            return
        self.isActive = active
        if active and HudButton.activated_sound is not None:
            HudButton.activated_sound.play()
        self._mark_dirty()
        self.redraw()


def _generate_hud_surfaces(hud_surface):
    hud_cell_surfaces = []
    cell_height = hud_surface.get_height() - renderer.VIEWPORT_Y_OFFSET//2
    cell_width = (hud_surface.get_width() -
                  (renderer.HUD_CELL_OFFSET + 1) * renderer.HUD_NUM_OF_CELLS)
    cell_width /= renderer.HUD_NUM_OF_CELLS
    surf_count = 0
    while surf_count < renderer.HUD_NUM_OF_CELLS:
        surf_count += 1
        window = HudButton(cell_width, cell_height)
        window.fill(colors.NAVY_BLUE)
        hud_cell_surfaces.append(window)
    return hud_cell_surfaces


def _generate_hud_viewport():
    renderer.get_screen()
    hud_width = renderer.SCREEN_WIDTH - renderer.VIEWPORT_X_OFFSET * 2
    hud_height = (renderer.SCREEN_HEIGHT -
                  renderer.VIEWPORT_HEIGHT -
                  renderer.VIEWPORT_Y_OFFSET * 2)

    hud_viewport = pygame.Surface([hud_width, hud_height]).convert()
    hud_viewport.fill(colors.BLUE)
    return hud_viewport


if __name__ == "__main__":
    import pygame
    pygame.init()

    clock = pygame.time.Clock()
    X = MapSelectionScreen()
    done = False
    X.draw()
    while not done:
        deltaTime = clock.get_time() / 1000
        fps = clock.get_fps()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        screen = renderer.get_screen()
        screen.fill(colors.BLACK)
        X.update(deltaTime, events)
        screen.blit(X, (0, 0))
        pygame.display.flip()
        clock.tick(60)
