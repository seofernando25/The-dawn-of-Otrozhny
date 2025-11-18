import textDraw
import pygame


def truncline(text, maxwidth, font):
    text = str(text)
    real = len(text)
    stext = text
    text_width = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while text_width > maxwidth:
        a = a + 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        text_width = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, pixel_max_width, size):
    done = 0
    wrapped = []
    if size in textDraw.font_cache:
        font = textDraw.font_cache[size]

    else:
        font = pygame.font.Font(textDraw.FONT_PATH, size)
    while not done:
        nl, done, stext = truncline(text, pixel_max_width, font)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


# Demo of text wrapping
if __name__ == "__main__":
    import ui
    import colors
    import pygame
    from renderer import config as renderer_settings

    pygame.init()
    screen = renderer_settings.get_screen()
    hudb = ui.HudButton(300, 200)
    hudb.set_text("THIS IS A TEST OF A REALLY BIG SENTENCE BEING WRAPPED")
    clock = pygame.time.Clock()
    import textDraw

    while 1:
        pygame.event.pump()
        screen.fill(colors.WHITE)
        hudb.set_active(True)
        screen.blit(hudb, (0, 0))
        pygame.display.flip()
        clock.tick(10)
