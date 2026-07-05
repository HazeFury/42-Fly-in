from typing import Dict, Tuple

import arcade

from core.graph import Hub


def get_bounding_box(hubs: Dict[str, Hub]) -> Tuple[int, int, int, int]:
    """
    Iterates through all hubs to find the extreme logical coordinates.
    Returns: (min_x, max_x, min_y, max_y)
    """
    if not hubs:
        return 0, 0, 0, 0

    # Initialize with the coordinates of the first hub we find
    first_hub = next(iter(hubs.values()))
    min_x = max_x = first_hub.x
    min_y = max_y = first_hub.y

    for hub in hubs.values():
        if hub.x < min_x:
            min_x = hub.x
        if hub.x > max_x:
            max_x = hub.x
        if hub.y < min_y:
            min_y = hub.y
        if hub.y > max_y:
            max_y = hub.y

    return min_x, max_x, min_y, max_y


def calculate_scale_factors(
    min_x: int,
    max_x: int,
    min_y: int,
    max_y: int,
    screen_width: int,
    screen_height: int,
    padding: int,
) -> Tuple[float, float]:
    """
    Calculates independent scale factors for X and Y axes
    to stretch the graph across the entire available screen space.
    """
    width_range = max(1, max_x - min_x)
    height_range = max(1, max_y - min_y)

    available_width = screen_width - (2 * padding)
    available_height = screen_height - (2 * padding)

    scale_x = available_width / width_range
    scale_y = available_height / height_range

    # Return both scales instead of just the minimum
    return scale_x, scale_y


def get_screen_coordinates(
    logical_x: int,
    logical_y: int,
    min_x: int,
    min_y: int,
    max_x: int,
    max_y: int,
    scale_x: float,
    scale_y: float,
    screen_width: int,
    screen_height: int,
) -> Tuple[float, float]:
    """
    Transforms logical graph coordinates into physical screen pixels
    using independent X and Y scales.
    """
    logical_center_x = (min_x + max_x) / 2
    logical_center_y = (min_y + max_y) / 2

    # Apply the specific scale to each axis
    offset_x = (logical_x - logical_center_x) * scale_x
    offset_y = (logical_y - logical_center_y) * scale_y

    screen_x = (screen_width / 2) + offset_x
    screen_y = (screen_height / 2) + offset_y

    return screen_x, screen_y


arcade_color_data = {
    "white": arcade.color.WHITE,
    "green": arcade.color.GREEN,
    "blue": arcade.color.BLUE,
    "gold": arcade.color.GOLD,
    "black": arcade.color.BLACK,
    "orange": arcade.color.ORANGE,
    "red": arcade.color.RED,
    "purple": arcade.color.PURPLE,
    "maroon": arcade.color.MAROON,
    "brown": arcade.color.BROWN,
    "darkred": arcade.color.DARK_RED,
    "violet": arcade.color.VIOLET,
    "crimson": arcade.color.CRIMSON,
    "rainbow": arcade.color.MULBERRY,
    "cyan": arcade.color.CYAN,
    "yellow": arcade.color.YELLOW,
    "lime": arcade.color.LIME,
    "magenta": arcade.color.MAGENTA,
}
