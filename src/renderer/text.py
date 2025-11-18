# Functions to draw text on the screen
from core import colors
import os
import pygame

DEFAULT_FONT_SIZE = 8

font_cache = {}
# Get the src directory (parent of renderer)
dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FONT_NAME = "ff.ttf"
FONT_PATH = os.path.join(dir_path, FONT_NAME)


def text_object(text, font, color=colors.WHITE):
    text_surface = font.render(str(text), True, color)
    return text_surface, text_surface.get_rect()


def message_display_L(screen, text, x, y, size=DEFAULT_FONT_SIZE, color=colors.WHITE):
    if size in font_cache:
        f = font_cache[size]
        text_surf, text_rect = text_object(text, f, color)
        text_rect.topleft = (x, y)
        return screen.blit(text_surf, text_rect)

    font = pygame.font.Font(FONT_PATH, size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.topleft = (x, y)
    font_cache[size] = font
    return screen.blit(text_surf, text_rect)


def message_display_R(screen, text, x, y, size=DEFAULT_FONT_SIZE, color=colors.WHITE):
    if size in font_cache:
        f = font_cache[size]
        text_surf, text_rect = text_object(text, f, color)
        text_rect.topleft = (x, y)
        return screen.blit(text_surf, text_rect)

    font = pygame.font.Font(FONT_PATH, size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.topright = (x, y)
    font_cache[size] = font
    return screen.blit(text_surf, text_rect)


def message_display_MB(screen, text, x, y, size=DEFAULT_FONT_SIZE, color=colors.WHITE):
    if size in font_cache:
        f = font_cache[size]
        text_surf, text_rect = text_object(text, f, color)
        text_rect.midbottom = (x, y)
        return screen.blit(text_surf, text_rect)

    font = pygame.font.Font(FONT_PATH, size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.midbottom = (x, y)
    font_cache[size] = font
    return screen.blit(text_surf, text_rect)


def message_display_MT(screen, text, x, y, size, color=colors.WHITE):
    if size in font_cache:
        f = font_cache[size]
        text_surf, text_rect = text_object(text, f, color)
        text_rect.midtop = (x, y)
        return screen.blit(text_surf, text_rect)

    font = pygame.font.Font(FONT_PATH, size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.midtop = (x, y)
    font_cache[size] = font
    return screen.blit(text_surf, text_rect)


def message_display(screen, text, x, y, size, color=colors.WHITE):
    if size in font_cache:
        f = font_cache[size]
        text_surf, text_rect = text_object(text, f, color)
        text_rect.center = (x, y)
        return screen.blit(text_surf, text_rect)

    font = pygame.font.Font(FONT_PATH, size)
    text_surf, text_rect = text_object(text, font, color)
    text_rect.center = (x, y)
    font_cache[size] = font
    return screen.blit(text_surf, text_rect)


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
    """Wrap text to fit within a pixel width."""
    done = 0
    wrapped = []
    if size in font_cache:
        font = font_cache[size]
    else:
        font = pygame.font.Font(FONT_PATH, size)
    while not done:
        nl, done, stext = truncline(text, pixel_max_width, font)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped

