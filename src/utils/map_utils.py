from collections import deque
from typing import Dict, Tuple

import arcade

from core.graph import Hub
from utils.models import LevelData


def get_bounding_box(hubs: Dict[str, Hub]) -> Tuple[int, int, int, int]:
    """
    Iterates through all hubs to find the extreme logical coordinates.
    Returns: (min_x, max_x, min_y, max_y)
    """
    if not hubs:
        return 0, 0, 0, 0

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

    offset_x = (logical_x - logical_center_x) * scale_x
    offset_y = (logical_y - logical_center_y) * scale_y

    screen_x = (screen_width / 2) + offset_x
    screen_y = (screen_height / 2) + offset_y

    return screen_x, screen_y


def verify_map(level_data: LevelData) -> bool:
    """
    Performs a Breadth-First Search (BFS) to determine if a valid path
    exists from the start_hub to the end_hub, avoiding blocked zones.
    """
    start_hub = None
    end_hub = None
    blocked_zones = set()

    for zone in level_data.zones:
        if zone.type == "start_hub":
            start_hub = zone.name
        elif zone.type == "end_hub":
            end_hub = zone.name

        if zone.metadata and zone.metadata.zone == "blocked":
            blocked_zones.add(zone.name)

    if not start_hub or not end_hub:
        return False

    adj_list: dict[str, list[str]] = {
        zone.name: [] for zone in level_data.zones
    }
    for conn in level_data.connections:
        adj_list[conn.from_hub].append(conn.to_hub)
        adj_list[conn.to_hub].append(conn.from_hub)

    queue = deque([start_hub])
    visited = {start_hub}

    while queue:
        current = queue.popleft()

        if current == end_hub:
            return True

        for neighbor in adj_list[current]:
            if neighbor not in visited and neighbor not in blocked_zones:
                visited.add(neighbor)
                queue.append(neighbor)

    return False


def get_drone_offset(
    drone_id: str, offset_amount: float = 6.0
) -> tuple[float, float]:
    """
    Calculates a deterministic visual offset based on the drone's ID.
    Uses modulo 4 to place drones in 4 different corners around a hub
    so they don't visually overlap.

    Args:
        drone_id: The string identifier of the drone (e.g., "D1", "D2").
        offset_amount: The distance in pixels to shift the sprite.

    Returns:
        A tuple containing the (offset_x, offset_y).
    """
    # Extract the integer from the ID
    try:
        # Assumes IDs are formatted like "D1", "D2", etc.
        drone_num = int(drone_id.replace("D", ""))
    except ValueError:
        drone_num = 0

    position_index = drone_num % 4

    if position_index == 0:
        return (-offset_amount, offset_amount)  # Top-Left
    elif position_index == 1:
        return (offset_amount, offset_amount)  # Top-Right
    elif position_index == 2:
        return (-offset_amount, -offset_amount)  # Bottom-Left
    else:
        return (offset_amount, -offset_amount)  # Bottom-Right


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
