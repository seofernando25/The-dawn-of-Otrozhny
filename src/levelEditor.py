# This mess is the thing I used to create levels faster
# press f5! It's standalone
# PS: The options and save/load button are not finished
import enum
from typing import ClassVar, Optional, Tuple

import pygame
import levelData
from levelData import Level
from entities.enemies import Enemy
from entities.items import Collectible, Gate, Key
from entities.player import Player
import rendering as renderer
import colors
import textDraw
import ui
import gameIO
from level_editor import tools as editor_tools
from gameState import GameState
from loops.loop_runner import SceneHandler, run_scene


def _current_level() -> Level:
    return levelData.require_current_map()


class EditorTools(enum.Enum):
    node_editor = 0
    drawing_mode = 1
    wall_editor = 2
    options = 3
    save_load = 4


class PencilType:
    player = 0
    enemy = 1
    node = 2


class GridManager:
    instance: ClassVar[Optional["GridManager"]] = None

    def __init__(self, grid_width, grid_height):
        self.verticalButtonIndex = 1
        self.horizontalButtonIndex = 0
        self.grid: list[list[int]] = [
            [0 for x in range(grid_width)] for y in range(grid_height)
        ]
        levelData.Level.currentMap = levelData.Level(self.grid, [], [])
        for y in range(grid_height):
            self.grid[y][0] = 1
            self.grid[y][grid_width - 1] = 1
        for y in range(grid_width):
            self.grid[0][y] = 1
            self.grid[grid_height - 1][y] = 1

        self.current_cell: Optional[Tuple[int, int]] = None
        self.scale = 50
        self.adjust: Tuple[float, float] = (0.0, 0.0)
        GridManager.instance = self
        self.current_tool = EditorTools.node_editor
        self.mouse_in_grid = False
        self.mouse_position: Tuple[int, int] = (0, 0)

        self.mouse_b = pygame.mouse.get_pressed()
        self.mouseRel: Optional[Tuple[int, int]] = None

        self.hud_draw_obj_help = ui.VerticalList(
            [
                "Z: Player",
                "X: Enemy",
                "C: Node",
                "V: Wall",
                "B: Coin",
                "F: Key",
                "G: Gate",
            ],
            renderer.SCREEN_WIDTH - 150,
            10,
        )
        self.hud_draw_pos_help = ui.VerticalList(
            ["(000, 000)", "1234567890123"], 10, 10
        )
        self.tools = {
            EditorTools.options: editor_tools.MoveTool(),
            EditorTools.drawing_mode: editor_tools.PlaceTool(),
            EditorTools.wall_editor: editor_tools.WallEditorTool(),
            EditorTools.node_editor: editor_tools.NodeTool(),
        }
        self.navigation_tool = editor_tools.NavigationTool()

    def setTool(self, toolType):
        self.current_tool = EditorTools(toolType)

    def update(self, events, keys, deltaTime):
        self.mouse_position = (0, 0)
        self.setTool(self.horizontalButtonIndex)

        # Handle tool shortcuts for placement
        if keys[pygame.K_z]:
            self.hud_draw_obj_help.objects[self.verticalButtonIndex].set_active(False)
            self.hud_draw_obj_help.objects[0].set_active(True)
            self.verticalButtonIndex = 0
        if keys[pygame.K_x]:
            self.hud_draw_obj_help.objects[self.verticalButtonIndex].set_active(False)
            self.verticalButtonIndex = 1
            self.hud_draw_obj_help.objects[1].set_active(True)
        if keys[pygame.K_c]:
            self.hud_draw_obj_help.objects[self.verticalButtonIndex].set_active(False)
            self.verticalButtonIndex = 2
            self.hud_draw_obj_help.objects[2].set_active(True)
        if keys[pygame.K_v]:
            self.hud_draw_obj_help.objects[self.verticalButtonIndex].set_active(False)
            self.verticalButtonIndex = 3
            self.hud_draw_obj_help.objects[3].set_active(True)
        if keys[pygame.K_b]:
            self.hud_draw_obj_help.objects[self.verticalButtonIndex].set_active(False)
            self.verticalButtonIndex = 4
            self.hud_draw_obj_help.objects[4].set_active(True)
        if keys[pygame.K_f]:
            self.hud_draw_obj_help.objects[self.verticalButtonIndex].set_active(False)
            self.verticalButtonIndex = 5
            self.hud_draw_obj_help.objects[5].set_active(True)
        if keys[pygame.K_g]:
            self.hud_draw_obj_help.objects[self.verticalButtonIndex].set_active(False)
            self.verticalButtonIndex = 6
            self.hud_draw_obj_help.objects[6].set_active(True)

        self.update_mouse_position()
        instance = GridManager.instance
        current_cell = (
            instance.current_cell if instance is not None else self.current_cell
        )
        current_tool_name = (
            instance.current_tool.name
            if instance is not None
            else self.current_tool.name
        )
        self.hud_draw_pos_help.objects[0].set_text(str(current_cell))
        self.hud_draw_pos_help.objects[1].set_text(str(current_tool_name))
        self.navigation_tool.update(events, keys, deltaTime, self)
        if self.scale < 2:
            self.scale = 2

        active_tool = self.tools.get(self.current_tool)
        if active_tool is not None:
            active_tool.update(events, keys, deltaTime, self)

    def update_mouse_position(self):
        self.mouse_b = pygame.mouse.get_pressed()
        self.mouseRel = pygame.mouse.get_rel()

        self.mouse_position = pygame.mouse.get_pos()

        cellX = self.mouse_position[0] - self.adjust[0]
        cellX = cellX // self.scale
        cellY = self.mouse_position[1] - self.adjust[1]
        cellY = cellY // self.scale
        if (
            cellX < 0
            or cellX >= len(self.grid[0])
            or cellY < 0
            or cellY >= len(self.grid)
        ):
            self.current_cell = None
            self.mouse_in_grid = False
        else:
            self.current_cell = (round(cellX), round(cellY))
            self.real_position = (cellX, cellY)
            self.mouse_in_grid = True

    def draw(self, screen):
        for x in range(len(self.grid[0])):
            for y in range(len(self.grid)):
                color_flag = self.grid[y][x]

                if color_flag == 0:
                    wall_color = colors.WHITE
                else:
                    wall_color = colors.ALMOST_BLACK

                if self.current_cell is not None and self.current_cell == (x, y):
                    wall_color = colors.multiply(wall_color, 0.5)

                pygame.draw.rect(
                    screen,
                    wall_color,
                    [
                        (x * self.scale + self.adjust[0]),
                        (y * self.scale + self.adjust[1]),
                        self.scale - 1,
                        self.scale - 1,
                    ],
                )

        count = 0
        for node in _current_level().node_entities:
            pygame.draw.rect(
                screen,
                colors.NAVY_BLUE,
                [
                    ((node.px - 0.5) * self.scale + self.adjust[0]),
                    ((node.py - 0.5) * self.scale + self.adjust[1] - 0.5),
                    self.scale - 1,
                    self.scale,
                ],
            )
            for otherNode in node.nodes:
                scaledStartX = int(node.px * self.scale + self.adjust[0])
                scaledStartY = int(node.py * self.scale + self.adjust[1])
                scaledEndX = int(otherNode.px * self.scale + self.adjust[0])
                scaledEndY = int(otherNode.py * self.scale + self.adjust[1])
                pygame.draw.line(
                    screen,
                    colors.NAVY_BLUE,
                    (scaledStartX, scaledStartY),
                    (scaledEndX, scaledEndY),
                    5,
                )
        for entity in _current_level().grid_entities:
            count += 1
            col = colors.ACCENTUADED_BLUE
            if issubclass(type(entity), Collectible):
                col = colors.YELLOW
            if issubclass(type(entity), Key):
                col = colors.PINK
            if issubclass(type(entity), Gate):
                col = colors.BLACK

            if issubclass(type(entity), Player):
                col = colors.GREEN
            elif issubclass(type(entity), Enemy):
                col = colors.DARK_GRAY
                if entity.patrolPoint is not None:
                    col = colors.RED

            pygame.draw.circle(
                screen,
                col,
                (
                    int(entity.px * self.scale + self.adjust[0]),
                    int(entity.py * self.scale + self.adjust[1]),
                ),
                int(self.scale / 2),
            )
            textDraw.message_display(
                screen,
                count,
                int(entity.px * self.scale + self.adjust[0]),
                int(entity.py * self.scale + self.adjust[1]),
                self.scale // 2,
                colors.WHITE,
            )

        tool = self.tools.get(self.current_tool)
        if tool is not None:
            tool.draw(screen, self)

        if self.current_tool == EditorTools.drawing_mode:
            self.hud_draw_obj_help.draw()

        self.hud_draw_pos_help.draw()


class EditorScene(SceneHandler):
    """Scene handler for the level editor loop."""

    def __init__(self):
        self.grid_manager = GridManager(20, 20)
        self.hud = ui.HudScreen()
        self.hud.set_button_text(0, "Node Editor")
        self.hud.set_button_text(1, "Draw  Mode")
        self.hud.set_button_text(2, "Wall Editor")
        self.hud.set_button_text(3, "Options")
        self.hud.set_button_text(4, "SAVE  LOAD")
        self.result = None
        self._last_events = []
        self._keys = pygame.key.get_pressed()

    def handle_events(self, events, keys_pressed):
        self._last_events = events
        self._keys = keys_pressed

        for event in events:
            if event.type == pygame.QUIT:
                self.result = GameState.Quit
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.result = GameState.Menu
                    return True
                if event.key == pygame.K_RETURN:
                    if self.hud.selected_button == 4:
                        lvl = levelData.Level(
                            self.grid_manager.grid,
                            _current_level().grid_entities,
                            _current_level().node_entities,
                        )
                        gameIO.save_level(str(id(lvl)), lvl)
                        self.result = GameState.Menu
                        return True
        return False

    def update(self, delta_time):
        self.hud.update(delta_time, self._last_events)
        self.grid_manager.update(self._last_events, self._keys, delta_time)
        self.grid_manager.horizontalButtonIndex = self.hud.selected_button

    def draw(self, screen):
        screen.fill(colors.BLACK)
        self.grid_manager.draw(screen)
        self.hud.draw()


def editorLoop(clock):
    scene = EditorScene()
    run_scene(scene, clock)
    return scene.result or GameState.Menu


if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    editorLoop(clock)
