# Just placed some draw functions here because
# otherwise it would become messy
import textDraw
import rendering as renderer
import colors
from entities.enemies import EnemyStatus


def _screen():
    return renderer.get_screen()


def render_tutorial_tab_1():
    textDraw.message_display_MB(
        _screen(),
        "Enemy Status",
        renderer.SCREEN_WIDTH//1.5, renderer.VIEWPORT_Y_OFFSET * 1.5,
        20, color=colors.RED)

    row = 0
    textDraw.message_display_L(
        _screen(),
        "Enemy status refers to various states of alert that",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "affect the behaviour of enemy soldiers.",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 2
    textDraw.message_display_L(
        _screen(),
        "NORMAL",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, EnemyStatus.Normal.value[1])

    textDraw.message_display_L(
        _screen(),
        "While in Normal mode, enemy soldiers will ",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "follow a set patrol route.",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Alert",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, EnemyStatus.Alert.value[1])

    textDraw.message_display_L(
        _screen(),
        "This is the state in which the player has",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "been discovered by enemy soldiers. ",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "enemy soldiers call for backup and attack.",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Evasion",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, EnemyStatus.Evasion.value[1])

    textDraw.message_display_L(
        _screen(),
        "Enemy soldiers will search the area",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "they last found the player",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Caution",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, EnemyStatus.Caution.value[1])

    textDraw.message_display_L(
        _screen(),
        "Enemy soldiers will search the vicinity",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "after losing sight of the player",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)


def render_tutorial_tab_2():
    textDraw.message_display_MB(
        _screen(),
        "Map Editor",
        renderer.SCREEN_WIDTH//1.5, renderer.VIEWPORT_Y_OFFSET * 1.5,
        20, color=colors.RED)

    row = 0
    textDraw.message_display_L(
        _screen(),
        "You can create and edit you levels in the level",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "editor. You can share maps through the maps folder.",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 2

    textDraw.message_display_L(
        _screen(),
        "NAV",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.YELLOW)

    textDraw.message_display_L(
        _screen(),
        "You can edit and change node conections.",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "Making soldiers follow a set patrol route.",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Draw",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.YELLOW)

    textDraw.message_display_L(
        _screen(),
        "In draw mode you can add and remove",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "walls, as well as enemies and nodes",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Wall",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.YELLOW)

    textDraw.message_display_L(
        _screen(),
        "You can paint walls and add keys to them",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Options",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.YELLOW)

    textDraw.message_display_L(
        _screen(),
        "You can edit the settings of your map ",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "such as width and height",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)


def render_tutorial_tab_3():
    textDraw.message_display_MB(
        _screen(),
        "Items and Objects",
        renderer.SCREEN_WIDTH//1.5, renderer.VIEWPORT_Y_OFFSET * 1.5,
        20, color=colors.RED)

    row = 0
    textDraw.message_display_L(
        _screen(),
        "While on missions, you may find a variety of ",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "items and obstacles",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 2

    textDraw.message_display_L(
        _screen(),
        "Keys",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.YELLOW)

    textDraw.message_display_L(
        _screen(),
        "Keys can open gates and allow you to",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "pass through before locked areas.",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Gates",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.YELLOW)

    textDraw.message_display_L(
        _screen(),
        "Gates block your path and may restrict",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "your way to an advantage point",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 2

    textDraw.message_display_L(
        _screen(),
        "Stars",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.YELLOW)

    textDraw.message_display_L(
        _screen(),
        "Are collectables scattered around the",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "map. You need to collect all of them to",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)

    row += 1

    textDraw.message_display_L(
        _screen(),
        "complete a mission",
        renderer.VIEWPORT_X_OFFSET * 10, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)


def render_tutorial_tab_4():
    textDraw.message_display_MB(
        _screen(),
        "Briefing",
        renderer.SCREEN_WIDTH//1.5, renderer.VIEWPORT_Y_OFFSET * 1.5,
        20, color=colors.RED)

    row = 0
    textDraw.message_display_L(
        _screen(),
        "JULY 2019: The human species is on the edge of",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "extinction. ",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 2
    textDraw.message_display_L(
        _screen(),
        "A geneticaly modified creature created by Kephart",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "corporations of Keter class named by SPC-610 was",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "recently denounced uncontained of level Red after",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "members from Area-683 lost direct contact to",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "I DATA EXPUNGED I . Locals from Otrozhny in the ",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "Russia Confederation also recently reported ",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "anomalous sounds comming from Area-683.",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 2
    textDraw.message_display_L(
        _screen(),
        "Fortunately, one of the officers was able to",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "contact HQ via a 2000 MK VI Transreciever.",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "More details will be availible ASAP",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "I End of transmission I",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)


def render_tutorial_tab_5():
    textDraw.message_display_MB(
        _screen(),
        "Unauthorized",
        renderer.SCREEN_WIDTH//1.5, renderer.VIEWPORT_Y_OFFSET * 1.5,
        20, color=colors.RED)

    row = 0
    textDraw.message_display_L(
        _screen(),
        "Error 401 - Unauthorized",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, colors.RED)
    row += 2
    textDraw.message_display_L(
        _screen(),
        "You do not have permission to view this directory",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12, color=colors.RED)
    row += 2
    textDraw.message_display_L(
        _screen(),
        "olssv, ty ztpao",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "pm fvb hyl zllpun aopz tlzzhnl jvunyhabshapvuz.",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "bumvyabuhalsf, aol zavyf pz zapss pujvtwslal ",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "huk pa thf ulcly dpss p zhk ltvqp p . wslhzl ",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
    row += 1
    textDraw.message_display_L(
        _screen(),
        "jvtl ihjr shaly.",
        renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET * 2 + 20 * row,
        12)
