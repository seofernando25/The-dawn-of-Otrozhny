import enum

class GameState(enum.Enum):
    Menu = -1
    Play = 0
    Edit = 1
    Tutorial = 2
    About = 3
    Quit = 4