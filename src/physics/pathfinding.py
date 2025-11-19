import heapq
import math
from collections.abc import Iterator
from collections.abc import Sequence

# See: http://www.sfu.ca/~arashr/warren.pdf


def go_to(
    start: tuple[int, int],
    target: tuple[int, int],
    grid: Sequence[Sequence[int]],
) -> list[tuple[int, int]] | None:
    open_heap: list[tuple[int, tuple[int, int]]] = []
    heapq.heappush(open_heap, (get_heuristic(start, target), start))
    cameFrom: dict[tuple[int, int], tuple[int, int]] = {}
    gScore: dict[tuple[int, int], int] = {start: 0}
    closed_set: set[tuple[int, int]] = set()

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

    return None


# Get NSEW neighboors if possible


def get_neighbors(
    coord: tuple[int, int], grid: Sequence[Sequence[int]]
) -> Iterator[tuple[int, int]]:
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


def get_heuristic(coord: tuple[int, int], end: tuple[int, int]) -> int:
    dx = abs(coord[0] - end[0])
    dy = abs(coord[1] - end[1])
    return dx + dy


def reconstruct_path(
    cameFrom: dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]
) -> list[tuple[int, int]]:
    result = [current]
    while current in cameFrom:
        current = cameFrom[current]
        result.append(current)
    return list(reversed(result))
