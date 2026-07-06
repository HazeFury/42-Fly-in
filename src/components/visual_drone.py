import math
from typing import List, Optional, Tuple

import arcade


class VisualDrone(arcade.Sprite):
    """
    A smart sprite that handles its own movement queue to prevent
    corner-cutting during rapid simulation updates.
    """

    def __init__(self, filename: str, scale: float) -> None:
        super().__init__(filename, scale)

        # Queue storing: (target_x, target_y, requested_travel_time)
        self.waypoints: List[Tuple[float, float, float]] = []

        # Current physical destination
        self.target_x: Optional[float] = None
        self.target_y: Optional[float] = None

        # Required speed to reach the current target on time
        self.current_speed: float = 0.0

    def move_to(
        self, target_x: float, target_y: float, travel_time: float = 0.5
    ) -> None:
        """
        Instead of teleporting or overriding the current path,
        we queue the new destination.
        """
        self.waypoints.append((target_x, target_y, travel_time))

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        """
        Handles smooth movement along the queued waypoints.
        Automatically accelerates if falling behind the logical simulation.
        """
        # 1. Fetch the next waypoint if the drone is idling
        if self.target_x is None and self.waypoints:
            self.target_x, self.target_y, travel_time = self.waypoints.pop(0)

            # Calculate required speed (pixels per second) to arrive strictly
            # on time
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            distance = math.sqrt(dx**2 + dy**2)

            # Prevent division by zero if travel_time is magically 0
            safe_time = max(0.01, travel_time)
            self.current_speed = distance / safe_time

        # 2. Move towards the current target
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            distance = math.sqrt(dx**2 + dy**2)

            # Magic trick: The drone accelerates if there is a traffic jam of
            # waypoints!
            # Example: 0 waiting = 1x speed. 2 waiting = 3x speed.
            speed_multiplier = 1.0 + len(self.waypoints)
            move_amount = self.current_speed * speed_multiplier * delta_time

            # If the step is bigger than the remaining distance, snap exactly
            # to target
            if distance <= move_amount:
                self.center_x = self.target_x
                self.center_y = self.target_y

                # Clear target to trigger fetching the next waypoint on next
                # frame
                self.target_x = None
                self.target_y = None
            else:
                # Standard trigonometry to move along the vector
                angle = math.atan2(dy, dx)
                self.center_x += math.cos(angle) * move_amount
                self.center_y += math.sin(angle) * move_amount
