import heapq
import math

import pygame
import levelData

import colors
import mathHelpers
from renderer import config as renderer_settings

# See: http://www.sfu.ca/~arashr/warren.pdf


def go_to(start, target):
    grid = levelData.require_current_map().grid

    open_heap = []
    heapq.heappush(open_heap, (get_heuristic(start, target), start))
    cameFrom = {}
    gScore = {start: 0}
    closed_set = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in closed_set:
            continue
        if current == target:
            return reconstruct_path(cameFrom, current)

        closed_set.add(current)

        for neighbor in get_neighbors(current, grid):
            if neighbor in closed_set:
                continue

            tentative_gScore = gScore[current] + 1
            if tentative_gScore >= gScore.get(neighbor, math.inf):
                continue

            cameFrom[neighbor] = current
            gScore[neighbor] = tentative_gScore
            f_score = tentative_gScore + get_heuristic(neighbor, target)
            heapq.heappush(open_heap, (f_score, neighbor))

# Get NSEW neighboors if possible


def get_neighbors(coord, grid):
    map_w = len(grid[0])
    map_h = len(grid)
    coord = (int(coord[0]), int(coord[1]))
    if 0 < coord[0] - 1 < map_w:
        if grid[coord[0] - 1][coord[1]] == 0:
            yield (coord[0] - 1, coord[1])
    if 0 < coord[0] + 1 < map_w:
        if grid[coord[0] + 1][coord[1]] == 0:
            yield (coord[0] + 1, coord[1])

    if 0 < coord[1] + 1 < map_h:
        if grid[coord[0]][coord[1] + 1] == 0:
            yield (coord[0], coord[1] + 1)
    if 0 < coord[1] - 1 < map_h:
        if grid[coord[0]][coord[1] - 1] == 0:
            yield (coord[0], coord[1] - 1)


def get_heuristic(coord, end):
    dx = abs(coord[0] - end[0])
    dy = abs(coord[1] - end[1])
    return dx + dy


def reconstruct_path(cameFrom, current):
    result = [current]
    while current in cameFrom:
        current = cameFrom[current]
        result.append(current)
    return list(reversed(result))


if __name__ == "__main__":
    print("Pathfinding Example")
    SCREEN_WIDTH = renderer_settings.SCREEN_WIDTH
    SCREEN_HEIGHT = renderer_settings.SCREEN_HEIGHT

    SCREEN_SIZE = renderer_settings.SCREEN_SIZE

    screen = renderer_settings.get_screen()
    clock = pygame.time.Clock()
    done = False

    start = (2, 2)
    target = (14, 14)

    demo_grid = levelData.require_current_map().grid

    cached_result = go_to(start, target)

    temp_result = cached_result.copy()
    temp_result_temp = temp_result.copy()
    w = SCREEN_WIDTH / len(demo_grid[0])
    h = SCREEN_HEIGHT / len(demo_grid)

    while not done:
        deltaTime = clock.get_time() / 1000
        fps = clock.get_fps()
        mouse = pygame.mouse.get_pos()
        events = pygame.event.get()
        kb = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                start = (int(mouse[0]//w), int(mouse[1]//h))
                cached_result = go_to(start, target)
                temp_result = cached_result.copy()
                temp_result_temp = temp_result.copy()

        if len(temp_result) > 0:
            nextStep = temp_result[0]
            newX = mathHelpers.lerp(start[0], nextStep[0], deltaTime * 10)
            newY = mathHelpers.lerp(start[1], nextStep[1], deltaTime * 10)
            if (round(newX), round(newY)) == nextStep:
                temp_result.pop(0)
            start = (newX, newY)
        else:
            temp_result = temp_result_temp.copy()
            start = temp_result_temp[0]

        screen.fill(colors.WHITE)

        for x in range(len(demo_grid[0])):
            for y in range(len(demo_grid)):

                color_flag = demo_grid[x][y]

                if color_flag == 0:
                    wall_color = colors.WHITE
                else:
                    wall_color = colors.BLACK

                pygame.draw.rect(screen, wall_color, [(x*w), (y*h), w-1, h-1])

        for x, y in cached_result:
            pygame.draw.rect(screen, colors.GREEN, [
                             int(x*w), int(y*h), w-1, h-1])

        pygame.draw.circle(screen, colors.BLUE, [int(
            start[0] * w + w/2), int(start[1] * h + h/2)], 10)
        pygame.draw.circle(screen, colors.RED, [int(
            target[0] * w + (w/2)), int(target[1] * h + (h/2))], 10)

        pygame.display.update()
        clock.tick(60)
