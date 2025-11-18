"""
Level editor tools - modular tool classes for level editor operations.

Breaks down the monolithic GridManager into smaller, focused tool classes.
Each tool handles its own input/update/draw logic.
"""

import pygame
import rendering as renderer
import colors
from entities.enemies import Enemy, Node
import levelData
from levelData import Level


def _current_map() -> Level:
    return levelData.require_current_map()


class BaseTool:
    """Base class for level editor tools."""

    def __init__(self):
        self.name = "Base Tool"

    def update(self, events, keys, delta_time, grid_manager):
        """Update tool state. Return True if should quit."""
        pass

    def draw(self, screen, grid_manager):
        """Draw tool-specific UI elements."""
        pass

    def get_cursor_cell(self, mouse_pos, grid_manager):
        """Get grid cell under cursor."""
        cellX = mouse_pos[0] - grid_manager.adjust[0]
        cellX = cellX // grid_manager.scale
        cellY = mouse_pos[1] - grid_manager.adjust[1]
        cellY = cellY // grid_manager.scale

        if (
            cellX < 0
            or cellX >= len(grid_manager.grid[0])
            or cellY < 0
            or cellY >= len(grid_manager.grid)
        ):
            return None

        return round(cellX), round(cellY)


class MoveTool(BaseTool):
    """Tool for moving entities around the level."""

    def __init__(self):
        super().__init__()
        self.name = "Options"
        self.selected_entity = None

    def update(self, events, keys, delta_time, grid_manager):
        mouse_pos = pygame.mouse.get_pos()
        current_cell = self.get_cursor_cell(mouse_pos, grid_manager)

        if pygame.mouse.get_pressed()[0]:
            if self.selected_entity is None and current_cell:
                # Try to select an entity at current cell
                for entity in _current_map().grid_entities:
                    if current_cell == (int(entity.px), int(entity.py)):
                        self.selected_entity = entity
                        return

            if self.selected_entity and current_cell:
                # Move selected entity
                position_adjust = (current_cell[0] + 0.5, current_cell[1] + 0.5)
                self.selected_entity.px = position_adjust[0]
                self.selected_entity.py = position_adjust[1]
                self.selected_entity.patrolPoint = None  # Clear patrol point
        else:
            self.selected_entity = None

    def draw(self, screen, grid_manager):
        if self.selected_entity:
            pygame.draw.circle(
                screen,
                colors.ACCENTUADED_BLUE,
                (
                    int(
                        self.selected_entity.px * grid_manager.scale
                        + grid_manager.adjust[0]
                    ),
                    int(
                        self.selected_entity.py * grid_manager.scale
                        + grid_manager.adjust[1]
                    ),
                ),
                grid_manager.scale,
                2,
            )


class PlaceTool(BaseTool):
    """Tool for placing entities on the grid."""

    def __init__(self):
        super().__init__()
        self.name = "Draw Mode"
        self.object_to_place = None
        self.current_type_index = 0
        self.entity_types = [
            "Player",
            "Enemy",
            "Node",
            "Wall",
            "Collectible",
            "Key",
            "Gate",
        ]
        self.entity_classes = [
            None,
            None,
            Node,
            None,
            None,
            None,
            None,
        ]  # Will be imported

    def update(self, events, keys, delta_time, grid_manager):
        # Handle keyboard input for type selection
        for i, key in enumerate(
            [
                pygame.K_z,
                pygame.K_x,
                pygame.K_c,
                pygame.K_v,
                pygame.K_b,
                pygame.K_f,
                pygame.K_g,
            ]
        ):
            if keys[key]:
                self.current_type_index = i
                grid_manager.hud_draw_obj_help.objects[
                    self.current_type_index
                ].set_active(True)
                # Deactivate others
                for j, obj in enumerate(grid_manager.hud_draw_obj_help.objects):
                    if j != self.current_type_index and j < len(
                        grid_manager.hud_draw_obj_help.objects
                    ):
                        obj.set_active(False)

        mouse_pos = pygame.mouse.get_pos()
        current_cell = self.get_cursor_cell(mouse_pos, grid_manager)

        if current_cell:
            if pygame.mouse.get_pressed()[0]:  # Left click - place
                self.place_entity_at(current_cell, grid_manager)
            elif pygame.mouse.get_pressed()[2]:  # Right click - remove
                self.remove_entity_at(current_cell, grid_manager)

    def place_entity_at(self, cell, grid_manager):
        from entities.player import Player
        from entities.enemies import Monster, Node
        from entities.items import Collectible, Key, Gate

        position_adjust = (cell[0] + 0.5, cell[1] + 0.5)

        if self.current_type_index == 0:  # Player
            self.object_to_place = Player(position_adjust)
        elif self.current_type_index == 1:  # Enemy
            self.object_to_place = Monster(position_adjust)
        elif self.current_type_index == 2:  # Node
            self.object_to_place = Node(position_adjust)
        elif self.current_type_index == 3:  # Wall
            grid_manager.grid[cell[1]][cell[0]] = 1
            return
        elif self.current_type_index == 4:  # Collectible
            self.object_to_place = Collectible(position_adjust)
        elif self.current_type_index == 5:  # Key
            self.object_to_place = Key(position_adjust)
        elif self.current_type_index == 6:  # Gate
            self.object_to_place = Gate(position_adjust)

        if self.object_to_place:
            current_map = _current_map()

            # Check for conflicts and place entity
            can_place = True
            if isinstance(
                self.object_to_place, (Player, Enemy, Collectible, Key, Gate)
            ):
                for entity in current_map.grid_entities:
                    if cell == (int(entity.px), int(entity.py)):
                        can_place = False
                        break

            if isinstance(self.object_to_place, Node):
                for node in current_map.node_entities:
                    if cell == (int(node.px), int(node.py)):
                        can_place = False
                        break

            if can_place:
                if isinstance(self.object_to_place, Node):
                    current_map.node_entities.append(self.object_to_place)
                else:
                    current_map.grid_entities.append(self.object_to_place)

                # Connect enemies to nearby nodes
                if isinstance(self.object_to_place, Enemy):
                    for node in current_map.node_entities:
                        if (
                            abs(node.px - self.object_to_place.px) < 1.5
                            and abs(node.py - self.object_to_place.py) < 1.5
                        ):
                            self.object_to_place.patrolPoint = node
                            break

            self.object_to_place = None

    def remove_entity_at(self, cell, grid_manager):
        current_map = _current_map()

        # Remove wall
        grid_manager.grid[cell[1]][cell[0]] = 0

        # Remove entities at cell
        for entity in current_map.grid_entities[:]:
            if cell == (int(entity.px), int(entity.py)):
                current_map.grid_entities.remove(entity)

        for node in current_map.node_entities[:]:
            if cell == (int(node.px), int(node.py)):
                current_map.node_entities.remove(node)


class WallEditorTool(BaseTool):
    """Tool for editing walls on the grid."""

    def __init__(self):
        super().__init__()
        self.name = "Wall Editor"

    def update(self, events, keys, delta_time, grid_manager):
        mouse_pos = pygame.mouse.get_pos()
        current_cell = self.get_cursor_cell(mouse_pos, grid_manager)

        if current_cell:
            if pygame.mouse.get_pressed()[0]:  # Left click - place wall
                grid_manager.grid[current_cell[1]][current_cell[0]] = 1
            elif pygame.mouse.get_pressed()[2]:  # Right click - remove wall
                grid_manager.grid[current_cell[1]][current_cell[0]] = 0


class NodeTool(BaseTool):
    """Tool for connecting/disconnecting navigation nodes."""

    def __init__(self):
        super().__init__()
        self.name = "Node Editor"
        self.selected_node = None
        self.is_dragging = False

    def _find_node_at(self, cell):
        if cell is None:
            return None
        for node in _current_map().node_entities:
            if cell == (int(node.px), int(node.py)):
                return node
        return None

    def update(self, events, keys, delta_time, grid_manager):
        mouse_pos = pygame.mouse.get_pos()
        current_cell = self.get_cursor_cell(mouse_pos, grid_manager)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    node = self._find_node_at(current_cell)
                    if node is None:
                        self.selected_node = None
                        self.is_dragging = False
                    else:
                        if self.selected_node is None:
                            self.selected_node = node
                        elif node != self.selected_node:
                            self.selected_node.join_node(node)
                            self.selected_node = node
                        self.is_dragging = True
                elif event.button == 3:
                    node = self._find_node_at(current_cell)
                    if node is not None:
                        for other_node in node.nodes[:]:
                            node.remove_node(other_node)
                        if node == self.selected_node:
                            self.selected_node = None
                            self.is_dragging = False

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_dragging:
                    node = self._find_node_at(current_cell)
                    if node and self.selected_node and node != self.selected_node:
                        self.selected_node.join_node(node)
                        self.selected_node = node
                self.is_dragging = False

    def draw(self, screen, grid_manager):
        if self.selected_node:
            mouse_pos = pygame.mouse.get_pos()
            scaled_start_x = int(
                self.selected_node.px * grid_manager.scale + grid_manager.adjust[0]
            )
            scaled_start_y = int(
                self.selected_node.py * grid_manager.scale + grid_manager.adjust[1]
            )
            pygame.draw.line(
                screen, colors.NAVY_BLUE, (scaled_start_x, scaled_start_y), mouse_pos, 5
            )


class NavigationTool(BaseTool):
    """Tool for panning and zooming the level view."""

    def __init__(self):
        super().__init__()
        self.name = "Navigation"

    def update(self, events, keys, delta_time, grid_manager):
        # Handle zoom
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    grid_manager.scale += 1
                elif event.button == 5:  # Mouse wheel down
                    grid_manager.scale -= 1

        if grid_manager.scale < 2:
            grid_manager.scale = 2

        # Handle pan
        if keys[pygame.K_a]:
            grid_manager.adjust = (
                grid_manager.adjust[0] + delta_time * 50 * 20,
                grid_manager.adjust[1],
            )
        if keys[pygame.K_d]:
            grid_manager.adjust = (
                grid_manager.adjust[0] - delta_time * 50 * 20,
                grid_manager.adjust[1],
            )
        if keys[pygame.K_w]:
            grid_manager.adjust = (
                grid_manager.adjust[0],
                grid_manager.adjust[1] + delta_time * 50 * 20,
            )
        if keys[pygame.K_s]:
            grid_manager.adjust = (
                grid_manager.adjust[0],
                grid_manager.adjust[1] - delta_time * 50 * 20,
            )

        # Alt + drag - fine grained navigation
        if grid_manager.mouseRel is not None:
            mouse_buttons = pygame.mouse.get_pressed()
            mods = pygame.key.get_mods()
            if mouse_buttons[0] and (mods & pygame.KMOD_ALT):
                grid_manager.adjust = (
                    grid_manager.adjust[0] + grid_manager.mouseRel[0],
                    grid_manager.adjust[1] + grid_manager.mouseRel[1],
                )

        # Keep view in bounds
        grid_width = len(grid_manager.grid[0]) * grid_manager.scale
        grid_height = len(grid_manager.grid) * grid_manager.scale

        if grid_manager.adjust[0] < -grid_width:
            grid_manager.adjust = (
                renderer.SCREEN_WIDTH + grid_width,
                grid_manager.adjust[1],
            )
        elif grid_manager.adjust[0] > renderer.SCREEN_WIDTH + grid_width:
            grid_manager.adjust = (-grid_width, grid_manager.adjust[1])

        if grid_manager.adjust[1] < -grid_height:
            grid_manager.adjust = (
                grid_manager.adjust[0],
                renderer.SCREEN_HEIGHT + grid_height,
            )
        elif grid_manager.adjust[1] > renderer.SCREEN_HEIGHT + grid_height:
            grid_manager.adjust = (grid_manager.adjust[0], -grid_height)
