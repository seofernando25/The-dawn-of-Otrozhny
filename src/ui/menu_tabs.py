"""Menu tab rendering functions."""
from renderer.text import message_display_MB, message_display_L
from renderer import config as renderer_config
from renderer import utils as renderer_utils
from core import colors
from entities.base import EnemyStatus


def _screen():
    return renderer_config.get_screen()


def render_tutorial_tab_1():
    message_display_MB(
        _screen(),
        "Enemy Status",
        renderer_utils.SCREEN_WIDTH // 1.5,
        renderer_utils.VIEWPORT_Y_OFFSET * 1.5,
        20,
        color=colors.RED,
    )

    row = 0
    message_display_L(
        _screen(),
        "Enemy status refers to various states of alert that",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "affect the behaviour of enemy soldiers.",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 2
    message_display_L(
        _screen(),
        "NORMAL",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        EnemyStatus.Normal.value[1],
    )

    message_display_L(
        _screen(),
        "While in Normal mode, enemy soldiers will ",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "follow a set patrol route.",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Alert",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        EnemyStatus.Alert.value[1],
    )

    message_display_L(
        _screen(),
        "This is the state in which the player has",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "been discovered by enemy soldiers. ",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "enemy soldiers call for backup and attack.",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Evasion",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        EnemyStatus.Evasion.value[1],
    )

    message_display_L(
        _screen(),
        "Enemy soldiers will search the area",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "they last found the player",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Caution",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        EnemyStatus.Caution.value[1],
    )

    message_display_L(
        _screen(),
        "Enemy soldiers will search the vicinity",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "after losing sight of the player",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )


def render_tutorial_tab_2():
    message_display_MB(
        _screen(),
        "Map Editor",
        renderer_utils.SCREEN_WIDTH // 1.5,
        renderer_utils.VIEWPORT_Y_OFFSET * 1.5,
        20,
        color=colors.RED,
    )

    row = 0
    message_display_L(
        _screen(),
        "You can create and edit you levels in the level",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "editor. You can share maps through the maps folder.",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 2

    message_display_L(
        _screen(),
        "NAV",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.YELLOW,
    )

    message_display_L(
        _screen(),
        "You can edit and change node conections.",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "Making soldiers follow a set patrol route.",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Draw",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.YELLOW,
    )

    message_display_L(
        _screen(),
        "In draw mode you can add and remove",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "walls, as well as enemies and nodes",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Wall",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.YELLOW,
    )

    message_display_L(
        _screen(),
        "You can paint walls and add keys to them",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Options",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.YELLOW,
    )

    message_display_L(
        _screen(),
        "You can edit the settings of your map ",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "such as width and height",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )


def render_tutorial_tab_3():
    message_display_MB(
        _screen(),
        "Items and Objects",
        renderer_utils.SCREEN_WIDTH // 1.5,
        renderer_utils.VIEWPORT_Y_OFFSET * 1.5,
        20,
        color=colors.RED,
    )

    row = 0
    message_display_L(
        _screen(),
        "While on missions, you may find a variety of ",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "items and obstacles",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 2

    message_display_L(
        _screen(),
        "Keys",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.YELLOW,
    )

    message_display_L(
        _screen(),
        "Keys can open gates and allow you to",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "pass through before locked areas.",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Gates",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.YELLOW,
    )

    message_display_L(
        _screen(),
        "Gates block your path and may restrict",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "your way to an advantage point",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 2

    message_display_L(
        _screen(),
        "Stars",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.YELLOW,
    )

    message_display_L(
        _screen(),
        "Are collectables scattered around the",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "map. You need to collect all of them to",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

    row += 1

    message_display_L(
        _screen(),
        "complete a mission",
        renderer_utils.VIEWPORT_X_OFFSET * 10,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )


def render_tutorial_tab_4():
    message_display_MB(
        _screen(),
        "Briefing",
        renderer_utils.SCREEN_WIDTH // 1.5,
        renderer_utils.VIEWPORT_Y_OFFSET * 1.5,
        20,
        color=colors.RED,
    )

    row = 0
    message_display_L(
        _screen(),
        "JULY 2019: The human species is on the edge of",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "extinction. ",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 2
    message_display_L(
        _screen(),
        "A geneticaly modified creature created by Kephart",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "corporations of Keter class named by SPC-610 was",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "recently denounced uncontained of level Red after",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "members from Area-683 lost direct contact to",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "I DATA EXPUNGED I . Locals from Otrozhny in the ",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "Russia Confederation also recently reported ",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "anomalous sounds comming from Area-683.",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 2
    message_display_L(
        _screen(),
        "Fortunately, one of the officers was able to",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "contact HQ via a 2000 MK VI Transreciever.",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "More details will be availible ASAP",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "I End of transmission I",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )


def render_tutorial_tab_5():
    message_display_MB(
        _screen(),
        "Unauthorized",
        renderer_utils.SCREEN_WIDTH // 1.5,
        renderer_utils.VIEWPORT_Y_OFFSET * 1.5,
        20,
        color=colors.RED,
    )

    row = 0
    message_display_L(
        _screen(),
        "Error 401 - Unauthorized",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        colors.RED,
    )
    row += 2
    message_display_L(
        _screen(),
        "You do not have permission to view this directory",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
        color=colors.RED,
    )
    row += 2
    message_display_L(
        _screen(),
        "olssv, ty ztpao",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "pm fvb hyl zllpun aopz tlzzhnl jvunyhabshapvuz.",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "bumvyabuhalsf, aol zavyf pz zapss pujvtwslal ",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "huk pa thf ulcly dpss p zhk ltvqp p . wslhzl ",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )
    row += 1
    message_display_L(
        _screen(),
        "jvtl ihjr shaly.",
        renderer_utils.VIEWPORT_X_OFFSET,
        renderer_utils.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12,
    )

