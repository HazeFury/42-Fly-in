import arcade


class VisualDrone(arcade.Sprite):
    """
    A dumb visual component that smoothly animates from point A to point B
    using linear interpolation (Lerp), independent of the frame rate.
    """

    def __init__(self, image_path: str, scale: float = 1.0) -> None:
        super().__init__(image_path, scale)

        # State variables for movement
        self.is_moving: bool = False
        self.progress: float = 0.0
        self.speed: float = 1.0  # 1.0 means it takes exactly 1 second to
        # reach destination

        # Coordinates
        self.start_x: float = 0.0
        self.start_y: float = 0.0
        self.target_x: float = 0.0
        self.target_y: float = 0.0

    def move_to(
        self, target_x: float, target_y: float, travel_time: float = 1.0
    ) -> None:
        """
        Orders the sprite to move to a new location.
        """
        self.start_x = self.center_x
        self.start_y = self.center_y
        self.target_x = target_x
        self.target_y = target_y

        # If travel_time is 2 seconds, speed becomes 0.5 (it fills progress
        # at 50% per sec)
        self.speed = 1.0 / max(0.001, travel_time)
        self.progress = 0.0
        self.is_moving = True

    def update(self, delta_time: float = 1 / 60) -> None:
        """
        Called every frame. Advances the progress timer and calculates
        the new position.
        """
        if not self.is_moving:
            return

        # Increase progress based on real time
        self.progress += self.speed * delta_time

        # Clamp progress to 1.0 so we don't overshoot the target
        if self.progress >= 1.0:
            self.progress = 1.0
            self.is_moving = False

        # Apply the Lerp formula for X and Y axes
        self.center_x = (
            self.start_x + (self.target_x - self.start_x) * self.progress
        )
        self.center_y = (
            self.start_y + (self.target_y - self.start_y) * self.progress
        )
