"""Floor rendering for first-person view."""
from core import colors


def render_floor(screen, entity):
    """Render the floor/ceiling in the first-person view."""
    screen_height = screen.get_height()
    screen_width = screen.get_width()
    horizon = screen_height // 2
    floor_start = horizon + entity.angleY
    floor_start = max(0, min(screen_height, floor_start))
    if floor_start >= screen_height:
        return
    screen.fill(
        colors.DARK_GRAY,
        [(0, floor_start), (screen_width, screen_height - floor_start)],
    )

