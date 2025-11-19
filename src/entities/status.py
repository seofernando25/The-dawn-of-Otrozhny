from __future__ import annotations

import enum

from core import colors


class EnemyStatus(enum.Enum):
    Normal = ("Normal", colors.GREEN, 0)
    Alert = ("Alert", colors.RED, 10)
    Evasion = ("Evasion", colors.YELLOW, 20)
    Caution = ("Caution", colors.MAROON, 30)

