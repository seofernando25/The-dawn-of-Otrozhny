# Created by me: I
# PS: I wrote some really messy code
# on the other files to keep up with
# the deadlile. Anyway...hope you like
# the program
# :D

from pathlib import Path
import pygame
import colors
from entities.enemies import Enemy, EnemyStatus
from entities.player import Player
import rendering as renderer
import levelEditor
import textDraw
import levelData
import ui
import sys
import assets
import audio
import gameIO
from gameState import GameState

BASE_DIR = Path(__file__).resolve().parent

def tutorialLoop():
    import menuTabs
    done = False
    hud = ui.HudScreen()
    hud.set_button_text(0, "Briefing")
    hud.set_button_text(1, "Map Editor")
    hud.set_button_text(2, "Items")
    hud.set_button_text(3, "Enemy Status")
    hud.set_button_text(4, "?")
    hud.draw()
    while not done:
        deltaTime = clock.get_time() / 1000
        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                return GameState.Quit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return GameState.Menu

        screen = renderer.get_screen()
        screen.fill(colors.BLACK)

        if hud.selected_button == 0:
            menuTabs.render_tutorial_tab_4()
        if hud.selected_button == 1:
            menuTabs.render_tutorial_tab_2()
        if hud.selected_button == 2:
            menuTabs.render_tutorial_tab_3()
        if hud.selected_button == 3:
            menuTabs.render_tutorial_tab_1()
        if hud.selected_button == 4:
            menuTabs.render_tutorial_tab_5()

        hud.update(deltaTime, events)
        hud.draw()
        textDraw.message_display_L(screen, "Press \"q\" to go back",
                                   renderer.VIEWPORT_X_OFFSET,
                                   renderer.VIEWPORT_Y_OFFSET,
                                   renderer.HUD_CELL_TITLE_FONT_SIZE)

        pygame.display.update()
        clock.tick()


def aboutLoop():
    done = False
    sub_title_size = 1
    second_sub_title_size = 1
    while not done:
        deltaTime = clock.get_time() / 1000

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                return GameState.Quit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return GameState.Menu

        sub_title_size += deltaTime * 10
        if sub_title_size > 20:
            sub_title_size = 20
        screen = renderer.get_screen()
        screen.fill(colors.BLACK)
        if sub_title_size != 20:
            textDraw.message_display(screen,
                                     "Made By Fernando Nogueira",
                                     renderer.SCREEN_WIDTH // 2,
                                     renderer.VIEWPORT_Y_OFFSET, 20)
            textDraw.message_display(screen,
                                     "with some help from the internet",
                                     renderer.SCREEN_WIDTH // 2,
                                     renderer.VIEWPORT_Y_OFFSET * 2,
                                     int(sub_title_size))
        else:
            second_sub_title_size += deltaTime * 10
            if second_sub_title_size > 20:
                second_sub_title_size = 1
                sub_title_size = 1
            textDraw.message_display(screen, "Made By Stack Overflow",
                                     renderer.SCREEN_WIDTH // 2,
                                     renderer.VIEWPORT_Y_OFFSET, 20)
            textDraw.message_display(screen, "not really",
                                     renderer.SCREEN_WIDTH - 50,
                                     renderer.VIEWPORT_Y_OFFSET, 8)
            textDraw.message_display(screen,
                                     "with some help from fernando",
                                     renderer.SCREEN_WIDTH // 2,
                                     renderer.VIEWPORT_Y_OFFSET * 2,
                                     int(second_sub_title_size))

        textDraw.message_display_L(
            screen, "Press \"q\" to go back",
            renderer.VIEWPORT_X_OFFSET,
            renderer.SCREEN_HEIGHT - renderer.VIEWPORT_Y_OFFSET,
            renderer.HUD_CELL_TITLE_FONT_SIZE)

        pygame.display.update()
        clock.tick()


def menuLoop():
    import ui
    import otherEffects
    done = False
    hud = ui.HudScreen()
    hud.set_button_text(0, "Play")
    hud.set_button_text(1, "Editor")
    hud.set_button_text(2, "Tutorial")
    hud.set_button_text(3, "About")
    hud.set_button_text(4, "Exit")
    flag = None
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)

    fractal = otherEffects.ChaosObject(
        (renderer.SCREEN_WIDTH // 2, (renderer.SCREEN_HEIGHT // 2) + 15), 225,
        3)
    s_field = otherEffects.StarField(renderer.SCREEN_SIZE)

    hud.onChangedButton.append(s_field.change_speed)
    while not done:
        deltaTime = clock.get_time() / 1000
        screen = renderer.get_screen()
        events = pygame.event.get()
        flag = hud.update(deltaTime, events)
        for event in events:

            if event.type == pygame.QUIT:
                return GameState.Quit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return GameState.Quit

        if hud.selected_button == GameState.Quit.value:
            s_field.speed += deltaTime * 75
            if s_field.speed > 100:
                s_field.speed = 100

        for x in range(10):
            fractal.update()

        s_field.update(deltaTime)

        # region Buttons

        s_field.draw()
        screen.blit(s_field, (0, 0))
        fractal.draw(screen)

        textDraw.message_display_MT(screen, "The dawn of Otrozhny",
                                    renderer.SCREEN_WIDTH // 2, 100, 30)
        textDraw.message_display_MT(screen, "Containment breach",
                                    renderer.SCREEN_WIDTH // 2, 150, 30)

        if flag is not None:
            return GameState(flag)

        hud.draw()
        pygame.display.update()
        clock.tick()


def setupGame():
    preLoadAssets()

    map_list = gameIO.list_maps()
    hud = ui.MapSelectionScreen()
    actual_map_list = [[None for _ in range(len(hud.hud_buttons[0]))]
                       for _ in range(len(hud.hud_buttons))]
    for px, button_list in enumerate(hud.hud_buttons):
        for py, button in enumerate(button_list):
            if len(map_list) > 0:
                map_path, _ = map_list.pop()
                map_obj = gameIO.load_level_object(map_path)
                actual_map_list[px][py] = map_obj
                renderer.draw_map_preview(button, map_obj, cache_key=map_path)
                button.redraw()
            else:
                break

    done = False
    while not done:
        deltaTime = clock.get_time() / 1000
        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                return GameState.Quit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if actual_map_list[hud.selected_button_x][
                            hud.selected_button_y] is not None:
                        mapObj = actual_map_list[hud.selected_button_x][
                            hud.selected_button_y]
                        levelData.Level.load(mapObj)
                        return gameLoop()
                elif event.key == pygame.K_q:
                    return GameState.Menu

        hud.update(deltaTime, events)

        screen = renderer.get_screen()
        screen.fill(colors.BLACK)
        hud.draw()
        textDraw.message_display_L(screen, "Press \"q\" to go back",
                                   renderer.VIEWPORT_X_OFFSET,
                                   renderer.VIEWPORT_Y_OFFSET,
                                   renderer.HUD_CELL_TITLE_FONT_SIZE)

        pygame.display.update()
        clock.tick()


def preLoadAssets():
    # Pre load all sprites in the game
    # See: LRU Cache documentation
    for pack in assets.list_asset_packs():
        assets.get_sprite(pack, 0)
    default_pack = assets.ASSETS_DIR / "Sprites"
    if default_pack.exists():
        assets.get_sprite("", 0)


def postGameLoop(won, time=0):
    import datetime
    done = False
    if won:
        elapsed_time = datetime.timedelta(seconds=time)
        msg = "You won"
    else:
        msg = "You lost"
        elapsed_time = None
    msg_accumulated = 0

    while not done:
        deltaTime = clock.get_time() / 1000

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                return GameState.Quit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return GameState.Quit

        msg_accumulated += deltaTime * 5
        if msg_accumulated > len(msg):
            msg_accumulated = len(msg)

        # region Buttons
        screen = renderer.get_screen()
        screen.fill(colors.BLACK)
        textDraw.message_display_MT(screen,
                                    msg[:int(msg_accumulated)],
                                    renderer.SCREEN_WIDTH // 2, 100, 30)
        textDraw.message_display_L(screen, "Press \"q\" to go back",
                                   renderer.VIEWPORT_X_OFFSET,
                                   renderer.VIEWPORT_Y_OFFSET,
                                   renderer.HUD_CELL_TITLE_FONT_SIZE)
        if won and elapsed_time is not None:
            textDraw.message_display_MT(
                screen,
                "{}.{}.{}".format(elapsed_time.seconds // 60,
                                  elapsed_time.seconds % 60,
                                  round(elapsed_time.microseconds / 1000)),
                renderer.SCREEN_WIDTH // 2, 150, 30)

        pygame.display.update()
        clock.tick()


def gameLoop():
    from renderer import minimap as renderer_minimap
    quit_intent = False
    hud = ui.HudScreen(interactable=False)
    hud.set_button_title(0, "Health")
    hud.set_button_title(1, "Stars")
    hud.set_button_subtitle(1, "Found")

    hud.set_button_title(2, "Keys")
    hud.set_button_title(3, "Status")

    #Allowing Loop to control hud button surface draw calls
    hud.hud_buttons[-1].protected = False
    try:
        player = Player.require_instance()
    except RuntimeError:
        return -1
    player.keys = 0
    Enemy.enemy_status = EnemyStatus.Normal
    Enemy.enemy_status_time_left = 0

    time = 0

    hud_cache = {
        "keys": None,
        "status_subtitle": None,
        "status_color": None,
        "status_time": None,
        "collectibles": None,
        "health": None,
    }

    def _update_hud_value(name, value, setter):
        if hud_cache.get(name) == value:
            return
        hud_cache[name] = value
        setter(value)

    while not quit_intent:
        deltaTime = clock.get_time() / 1000
        events = pygame.event.get()
        hud.update(deltaTime, events)
        kb = pygame.key.get_pressed()
        if kb[pygame.K_q]:
            return -1

        time += deltaTime

        if player.health <= 0:
            Enemy.enemy_status = EnemyStatus.Normal
            Enemy.enemy_status_time_left = 0
            return postGameLoop(False)

        current_map = levelData.require_current_map()
        if current_map.num_of_collected == current_map.num_of_collectibles:
            return postGameLoop(True, time)

        # Think
        for entity in current_map.grid_entities:
            entity.update(deltaTime, events)

        # region Rendering
        screen = renderer.get_screen()
        screen.fill(colors.BLACK)

        # region 3D View Rendering

        view_port = renderer.render_first_person_canvas(player)
        screen.blit(
            view_port,
            (renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET))

        # endregion

        # region Heads Up Display Rendering

        _update_hud_value("keys", player.keys, lambda v: hud.set_button_text(2, v))
        status_title = Enemy.enemy_status.value[0]
        status_color = Enemy.enemy_status.value[1]
        status_time = round(Enemy.enemy_status_time_left, 2)
        _update_hud_value("status_subtitle", status_title,
                          lambda v: hud.set_button_subtitle(3, v))
        _update_hud_value("status_color", status_color,
                          lambda v: hud.set_button_color(3, 1, v))
        _update_hud_value("status_time", status_time,
                          lambda v: hud.set_button_text(3, v))
        collectibles_text = "{} of {}".format(
            current_map.num_of_collected, current_map.num_of_collectibles)
        _update_hud_value("collectibles", collectibles_text,
                          lambda v: hud.set_button_text(1, v))
        _update_hud_value("health", int(player.health),
                          lambda v: hud.set_button_text(0, v))

        renderer_minimap.render_map(hud.hud_buttons[-1], player)

        hud.draw()

        # endregion

        # region Other Information
        textDraw.message_display_L(screen,
                                   "FPS: " + str(int(clock.get_fps())), 15, 10,
                                   15)

        textDraw.message_display_MT(
            screen,
            "X:" + str(round(player.px, 2)) + " Y: " +
            str(round(player.py, 2)),
            renderer.SCREEN_WIDTH // 2, 10, 15)
        # endregion
        # Flip FrameBuffer
        pygame.display.flip()
        # endregion

        clock.tick()


def preClose():
    pygame.quit()


def preInit():
    assets.get_cached_audio("Music", "Menu")
    assets.get_cached_audio("Music", "Game")
    ui.HudButton.activated_sound = assets.get_cached_audio(
        "Music", "Active_UI")


def mainLoop():
    audio.ensure_initialized()
    pygame.init()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
    pygame.display.set_caption('The dawn of Otrozhny')
    logo_path = BASE_DIR / "icon.png"
    logo = pygame.image.load(str(logo_path))
    pygame.display.set_icon(logo)
    #TODO do some kind of intro

    # Game Loop
    done = False
    preInit()
    music_channel = pygame.mixer.Channel(0)
    music_channel.play(assets.get_cached_audio("Music", "Menu"))

    while not done:
        if music_channel.get_sound() != assets.get_cached_audio(
                "Music", "Menu"):
            music_channel.stop()
            music_channel.play(assets.get_cached_audio("Music", "Menu"))

        state = menuLoop()

        if state == GameState.Quit:
            done = True
        elif state == GameState.Play:
            while state == GameState.Play:
                music_channel.stop()
                music_channel.play(assets.get_cached_audio("Music", "Game"))
                state = setupGame()

        elif state == GameState.About:
            while state == GameState.About:
                state = aboutLoop()

        elif state == GameState.Edit:
            while state == GameState.Edit:
                state = levelEditor.editorLoop(clock)

        elif state == GameState.Tutorial:
            while state == GameState.Tutorial:
                state = tutorialLoop()

    preClose()


# This is the program's entry point
if __name__ == "__main__":

    if sys.version_info.minor < 6:
        print("WARNING: Please use a newer version of cpython or pygame")
        print("Current python version is " + str(sys.version))

        print(
            "\nThis version may be unplayable due to a bug in the generate_distance_table function (on renderer.py)"
        )
        print("that cause floating points to be wronglly calculated")
        print(
            "\nOn my experience this bug only occured at 32bit machines with older versions of python and pygame"
        )

        print(
            "\nYou can disable this exception by commenting from line 290 to 302 in main.py"
        )
        print(
            "\nAfter updating your version please delete the __pycache__ folder"
        )
        input()

    clock = pygame.time.Clock()
    if len(sys.argv) > 1 and sys.argv[-1] == "PLOG":  #Performance log

        import cProfile
        import pstats
        import io
        #from pstats import SortKey
        print("Profiling...")
        pr = cProfile.Profile()
        pr.enable()
        mainLoop()
        pygame.quit()
        pr.disable()
        s = io.StringIO()
        #sortby = SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')
        ps.print_stats()
        fileStream = open("profile_stats.log", "w")
        fileStream.write(s.getvalue())
        fileStream.close()
    else:
        mainLoop()
