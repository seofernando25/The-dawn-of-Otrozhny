from dataclasses import dataclass
from entities.base import EnemyStatus


@dataclass
class EnemyStateManager:
    """Manages shared enemy status state across all enemies in the game.
    
    This is a global alert system where all enemies share the same status.
    When one enemy detects the player, all enemies become alert.
    """

    status: EnemyStatus = EnemyStatus.Normal
    status_time_left: float = 0.0

    def update(self, dt: float) -> None:
        """Update the shared enemy status timer. Call once per frame from game loop."""
        self.status_time_left -= dt
        if self.status_time_left < 0:
            self.status_time_left = 0
            if self.status == EnemyStatus.Alert:
                self.status = EnemyStatus.Evasion
            elif self.status == EnemyStatus.Evasion:
                self.status = EnemyStatus.Caution
            elif self.status == EnemyStatus.Caution:
                self.status = EnemyStatus.Normal

            if self.status != EnemyStatus.Normal:
                self.reset_status_time()

    def change_status(self, status: EnemyStatus) -> None:
        """Change the shared enemy status and reset the timer."""
        self.status = status
        self.status_time_left = status.value[2]

    def reset_status_time(self) -> None:
        """Reset the status timer to the current status's default duration."""
        self.status_time_left = self.status.value[2]

    def reset(self) -> None:
        """Reset the manager to normal state (used when starting a new game)."""
        self.status = EnemyStatus.Normal
        self.status_time_left = 0.0

