# Basic math functions
# Nothing to look here
import math
from utils import math_helpers


def point_circle_collision(point_pos, circle_pos, circle_radius):
    distX, distY = math_helpers.slope(point_pos, circle_pos)
    distance = math.hypot(distX, distY)
    return distance <= circle_radius
