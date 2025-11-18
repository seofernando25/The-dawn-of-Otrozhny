# This mess is the thing I used to create levels faster
# press f5! It's standalone
#PS: The options and save/load button are not finished
import pygame
import levelData
from entities.base import Agent, SpriteEntity
from entities.enemies import Enemy, Monster, Node
from entities.items import Collectible, Gate, Key
from entities.player import Player
import enum
import rendering as renderer
import colors
import textDraw
import ui
import gameIO
from gameState import GameState


def _current_level():
    return levelData.require_current_map()


class EditorTools(enum.Enum):
    node_editor = 0
    drawing_mode = 1
    wall_editor = 2
    options =3
    save_load =4
    

class PencilType():
    player = 0
    enemy = 1
    node = 2

class GridManager():
    instance = None
    def __init__(self, grid_width, grid_height):
        self.verticalButtonIndex = 1
        self.horizontalButtonIndex = 0
        self.grid = [[0 for x in range(grid_width)] for y in range(grid_height)] 
        levelData.Level.currentMap = levelData.Level(self.grid, [], [])
        for y in range(grid_height):
            self.grid[y][0] = 1
            self.grid[y][grid_width-1] = 1
        for y in range(grid_width):
            self.grid[0][y] = 1
            self.grid[grid_height-1][y] = 1

        self.current_cell = None
        self.scale = 50
        self.adjust = (0,0)
        GridManager.instance = self
        self.current_tool = EditorTools.node_editor
        self.mouse_in_grid = False 

        self.node_edit_start = None
        self.node_edit_end = None

        self.object_to_place = None
        self.clone_object = None
        self.current_entity_being_edited = None
        self.mouse_position = (0,0)

        self.alt_behaviour = False
        self.right_click_behaviour = False
        self.ctrl_behaviour = False

        self.mouse_b = pygame.mouse.get_pressed()
        self.mouseRel = None

        self.hud_draw_obj_help = ui.VerticalList(["Z: Player", "X: Enemy", "C: Node", "V: Wall", "B: Coin", "F: Key", "G: Gate"], renderer.SCREEN_WIDTH - 150, 10)
        self.hud_draw_pos_help = ui.VerticalList(["(000, 000)", "1234567890123"], 10, 10)

    def setTool(self, toolType): 
        self.current_tool = EditorTools(toolType)

    def update(self, events, keys, deltaTime):
        self.mouse_position = (0,0)
        mods = pygame.key.get_mods()
        self.setTool(self.horizontalButtonIndex)
        for event in events:  
            if event.type == pygame.QUIT:
                return -1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.scale += 1
                if event.button == 5:
                    self.scale -= 1
        if self.scale < 2:
            self.scale = 2

        if keys[pygame.K_a]:
            self.adjust = (self.adjust[0] + deltaTime * 50 * 20, self.adjust[1] )
        if keys[pygame.K_d]:
            self.adjust = (self.adjust[0] - deltaTime * 50 * 20, self.adjust[1] )
        if keys[pygame.K_w]:
            self.adjust = (self.adjust[0] , self.adjust[1]  + deltaTime  * 50 * 20)
        if keys[pygame.K_s]:
            self.adjust = (self.adjust[0], self.adjust[1]  - deltaTime  * 50 * 20 )

        # I should have created a function for that :/
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

        if self.mouse_b[2]:
            self.right_click_behaviour = True
        else:
            self.right_click_behaviour = False
        if mods & pygame.KMOD_ALT:

            self.alt_behaviour = True
        else:
            self.alt_behaviour = False
        
        if mods & pygame.KMOD_LCTRL:
            self.ctrl_behaviour = True
        else:
            self.ctrl_behaviour = False

        self.update_mouse_position()
        self.hud_draw_pos_help.objects[0].set_text(str(GridManager.instance.current_cell))
        self.hud_draw_pos_help.objects[1].set_text(str(GridManager.instance.current_tool.name))
        self.get_tool_behaviour()

        

    def get_tool_behaviour(self):
        # My super advanced state machine!!!
        if self.alt_behaviour and not (self.current_tool == EditorTools.options or self.current_tool == EditorTools.save_load) :
            self.navigation_intent()
            return

        if self.current_tool == EditorTools.wall_editor:
            if self.right_click_behaviour:
                self.remove_entity_intent()
            else:
                pass
        if self.current_tool == EditorTools.options:
            if self.mouse_b[0]: 
                self.move_entity_intent()
            else:
                self.current_entity_being_edited = None
        if self.current_tool == EditorTools.drawing_mode:
            if self.ctrl_behaviour:
                self.move_entity_intent()
            elif self.mouse_b[0]:
                self.place_entity_intent()
            elif self.right_click_behaviour:
                self.remove_entity_intent()
            
        if self.current_tool == EditorTools.node_editor:
            if not self.right_click_behaviour:
                self.join_nodes_intent()
            else:
                self.break_nodes_intent()
        if self.current_tool == EditorTools.save_load:
            #TODO: Allow user to type map name
            pass

    
    def join_nodes_intent(self):
        if self.mouse_in_grid:
            if self.mouse_b[0]:
                if self.node_edit_start is None:
                    for node in _current_level().node_entities:
                        if self.current_cell ==  (int(node.px), int(node.py)):
                            self.node_edit_start = node
                            return
                else:
                    self.node_edit_end = None
                    
            else:
                if self.node_edit_start is not None:
                    for node in _current_level().node_entities:
                        if self.current_cell ==  (int(node.px), int(node.py)) and node != self.node_edit_start:
                            self.node_edit_end = node
                            self.node_edit_start.join_node(self.node_edit_end)
                            self.node_edit_end = None
                            self.node_edit_start = None

                    self.node_edit_start = None
            
    
    def break_nodes_intent(self):
        if self.mouse_in_grid:
            for node in _current_level().node_entities:
                if self.current_cell ==  (int(node.px), int(node.py)):
                    for otherNode in node.nodes:
                        node.remove_node(otherNode)

    def move_entity_intent(self):
        # This should totally be simplified
        # but I would need to have a collision matrix
        # for players, enemies and nodes
        # eg: an entity can be over a node
        #     but an entity cant be over an entity
        if self.mouse_in_grid and self.mouse_b[0]:
            if self.current_entity_being_edited is None:
                for node in _current_level().node_entities:
                    if self.current_cell ==  (int(node.px), int(node.py)):
                        self.current_entity_being_edited = node
                        
                for entity in _current_level().grid_entities:
                    if self.current_cell ==  (int(entity.px), int(entity.py)):
                        self.current_entity_being_edited = entity

            if self.current_entity_being_edited is not None:
                position_adjust = (self.current_cell[0] + 0.5, self.current_cell[1] + 0.5)
                
                if hasattr(self.current_entity_being_edited, "patrolPoint"):
                    self.current_entity_being_edited.patrolPoint = None
                alreadyHas = False
                if issubclass(type(self.current_entity_being_edited), Agent):
                    for entity in _current_level().grid_entities:
                        if self.current_cell ==  (int(entity.px), int(entity.py)):
                            if issubclass(type(entity), Agent) and entity != self.current_entity_being_edited:
                                alreadyHas = True
                                if hasattr(self.current_entity_being_edited, "patrolPoint"):
                                    self.current_entity_being_edited.patrolPoint = None
                
                if issubclass(type(self.current_entity_being_edited), Enemy):
                    for node in _current_level().node_entities:  
                        if self.current_cell ==  (int(node.px), int(node.py)):
                            self.current_entity_being_edited.patrolPoint = node
                            for entity in _current_level().grid_entities:
                                if self.current_cell ==  (int(entity.px), int(entity.py)) and entity != self.current_entity_being_edited:
                                    self.current_entity_being_edited.patrolPoint = None

                elif issubclass(type(self.current_entity_being_edited), Node):
                    for entity in _current_level().grid_entities:
                        if self.current_cell ==  (int(entity.px), int(entity.py)):
                            if issubclass(type(entity), Enemy):
                                entity.patrolPoint = self.current_entity_being_edited
                            elif hasattr(entity, "patrolPoint") and entity.patrolPoint == self.current_entity_being_edited:
                                entity.patrolPoint = None
                if not alreadyHas:
                    self.current_entity_being_edited.px = position_adjust[0]
                    self.current_entity_being_edited.py = position_adjust[1]                    
        else:
            self.current_entity_being_edited = None

    def remove_entity_intent(self):
        if self.mouse_in_grid:
            self.grid[self.current_cell[0]][self.current_cell[1]] = 0
            for entity in _current_level().grid_entities:
                if self.current_cell ==  (int(entity.px), int(entity.py)):
                    _current_level().grid_entities.remove(entity)
            for node in _current_level().node_entities:  
                if self.current_cell ==  (int(node.px), int(node.py)):
                    _current_level().node_entities.remove(node)

    def place_wall_intent(self):
        self.grid[self.current_cell[0]][self.current_cell[1]] = 1
        

    def place_entity_intent(self):
        if self.mouse_in_grid:
            self.object_to_place = None
            position_adjust = (self.current_cell[0] + 0.5, self.current_cell[1] + 0.5)        
            if not self.right_click_behaviour:
                if self.verticalButtonIndex == 0:
                    self.object_to_place = Player(position_adjust)
                if self.verticalButtonIndex == 1:
                    self.object_to_place = Monster(position_adjust)
                    
                if self.verticalButtonIndex == 4:
                    self.object_to_place = Collectible(position_adjust)
                if self.verticalButtonIndex == 5:
                    self.object_to_place = Key(position_adjust)
                if self.verticalButtonIndex == 6:
                    self.object_to_place = Gate(position_adjust)

                if self.verticalButtonIndex == 2:
                    self.object_to_place = Node(position_adjust)
                if self.verticalButtonIndex == 3:
                    self.place_wall_intent()
                    return
        
                if self.object_to_place is not None:
                    if issubclass(type(self.object_to_place), SpriteEntity):   
                        for entity in _current_level().grid_entities:
                            if self.current_cell ==  (int(entity.px), int(entity.py)):
                                return
                        if issubclass(type(self.object_to_place), Enemy):   
                            for node in _current_level().node_entities:  
                                if self.current_cell ==  (int(node.px), int(node.py)):
                                        self.object_to_place.patrolPoint = node
                                        break
                        _current_level().grid_entities.append(self.object_to_place)
                    
                    if issubclass(type(self.object_to_place), Node):   
                        for node in _current_level().node_entities:  
                            if self.current_cell ==  (int(node.px), int(node.py)):
                                return
                        _current_level().node_entities.append(self.object_to_place)
                        
            else:
                self.remove_entity_intent()

    def navigation_intent(self):
        if self.mouse_b[0]:
            self.adjust = (self.adjust[0] + self.mouseRel[0], self.adjust[1] + self.mouseRel[1])
        

        if self.adjust[0] < -self.scale * (len(self.grid) ):
            self.adjust = (renderer.SCREEN_WIDTH +  self.scale * (len(self.grid)), self.adjust[1])
        if self.adjust[0] > renderer.SCREEN_WIDTH + self.scale * (len(self.grid)) :
            self.adjust = ( - self.scale  * (len(self.grid)) , self.adjust[1])
        if self.adjust[1] < -self.scale * ( len(self.grid)):
            self.adjust = (self.adjust[0], renderer.SCREEN_HEIGHT + self.scale * (len(self.grid)))
        if self.adjust[1] > renderer.SCREEN_HEIGHT + self.scale * len(self.grid):
            self.adjust = (self.adjust[0], -self.scale * len(self.grid))    
           
    def update_mouse_position(self):
        self.mouse_b = pygame.mouse.get_pressed()
        self.mouseRel = pygame.mouse.get_rel()
        
        self.mouse_position = pygame.mouse.get_pos()

        cellX = self.mouse_position[0] - self.adjust[0]
        cellX = cellX //  self.scale
        cellY = self.mouse_position[1] - self.adjust[1]
        cellY = cellY //  self.scale
        if (cellX < 0 or
                cellX >= len(self.grid[0])  or
                cellY < 0 or
                cellY >= len(self.grid) ):
            self.current_cell = None
            self.mouse_in_grid = False
        else:
            self.current_cell =  (round(cellX), round(cellY) )
            self.real_position = (cellX, cellY)
            self.mouse_in_grid = True

    
    def draw(self, screen):
        for x in range(len(self.grid[0])):
            for y in range(len(self.grid)):

                color_flag = self.grid[x][y]

                if color_flag == 0:
                    wall_color = colors.WHITE
                else:
                    wall_color = colors.ALMOST_BLACK

                if self.current_cell is not None and self.current_cell == (x,y):
                    wall_color = colors.multiply(wall_color, 0.5)

                pygame.draw.rect(screen, wall_color, [(x*self.scale + self.adjust[0]) , (y*self.scale + self.adjust[1]), self.scale-1, self.scale-1 ] )
        
        count = 0
        for node in _current_level().node_entities:  
            pygame.draw.rect(screen, colors.NAVY_BLUE, [( (node.px-0.5)*self.scale + self.adjust[0] ) , ( ( node.py -0.5)*self.scale + self.adjust[1] - 0.5), self.scale-1, self.scale ] )
            for otherNode in node.nodes:
                scaledStartX = int(node.px * self.scale + self.adjust[0])
                scaledStartY = int(node.py * self.scale + self.adjust[1])
                scaledEndX = int(otherNode.px * self.scale + self.adjust[0])
                scaledEndY = int(otherNode.py * self.scale + self.adjust[1])
                pygame.draw.line(screen, colors.NAVY_BLUE, (scaledStartX, scaledStartY) , (scaledEndX, scaledEndY), 5)
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

            pygame.draw.circle(screen, col, ( int(entity.px*self.scale + self.adjust[0]), int(entity.py*self.scale + self.adjust[1]) ), int(self.scale/2))
            textDraw.message_display(screen, count, int(entity.px*self.scale + self.adjust[0]) ,int(entity.py*self.scale + self.adjust[1]) , self.scale//2, colors.WHITE)
        
        if self.node_edit_start is not None:
            scaledStartX = int(self.node_edit_start.px * self.scale + self.adjust[0])
            scaledStartY = int(self.node_edit_start.py * self.scale + self.adjust[1])
            scaledEndX = self.mouse_position[0]
            scaledEndY = self.mouse_position[1]
            pygame.draw.line(screen, colors.NAVY_BLUE, (scaledStartX, scaledStartY) , (scaledEndX, scaledEndY), 5)

        if self.current_tool == EditorTools.drawing_mode:
            self.hud_draw_obj_help.draw()

        self.hud_draw_pos_help.draw()

def editorLoop(clock):
    done = False

    grid_manager = GridManager(20, 20)
    hud = ui.HudScreen()
    hud.set_button_text(0, "Node Editor")
    hud.set_button_text(1, "Draw  Mode")
    hud.set_button_text(2, "Wall Editor")
    hud.set_button_text(3, "Options")
    hud.set_button_text(4, "SAVE  LOAD")

    
    while not done:
        deltaTime = clock.get_time() / 1000
        keys = pygame.key.get_pressed()
        events = pygame.event.get() 
        kb = pygame.key.get_pressed()
        hud.update(deltaTime, events)       
        grid_manager.update(events, keys, deltaTime)
        for event in events:  
            if event.type == pygame.QUIT:
                return GameState.Quit
        if kb[pygame.K_q]:
            return GameState.Menu
        
        if kb[pygame.K_RETURN]:
            if hud.selected_button == 3:
                pass
            if hud.selected_button == 4:
                lvl = levelData.Level(grid_manager.grid, _current_level().grid_entities, _current_level().node_entities)
                gameIO.save_level(str(id(lvl)) , lvl)
                return GameState.Menu

        grid_manager.horizontalButtonIndex = hud.selected_button
        
        
        screen = renderer.get_screen()
        screen.fill(colors.BLACK)

        grid_manager.draw(screen)
        
        hud.draw()
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    editorLoop(clock)