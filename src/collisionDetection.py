# Basic math functions
# Nothing to look here
import math
import mathHelpers

def point_circle_collision(point_pos, circle_pos, circle_radius):
    distX, distY = mathHelpers.slope(point_pos, circle_pos) 
    distance = math.hypot(distX, distY)
    return distance <= circle_radius


