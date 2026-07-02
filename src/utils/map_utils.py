from typing import Dict, Tuple
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


def calculate_scale_factor(
    min_x: int, max_x: int, min_y: int, max_y: int,
    screen_width: int, screen_height: int, padding: int
) -> float:
    """
    Calculates the uniform scale factor to fit the graph within the screen.
    """
    width_range = max(1, max_x - min_x)
    height_range = max(1, max_y - min_y)

    available_width = screen_width - (2 * padding)
    available_height = screen_height - (2 * padding)

    scale_x = available_width / width_range
    scale_y = available_height / height_range

    return min(scale_x, scale_y)


def get_screen_coordinates(
    logical_x: int, logical_y: int,
    min_x: int, min_y: int, max_x: int, max_y: int,
    scale: float, screen_width: int, screen_height: int
) -> Tuple[float, float]:
    """
    Transforms logical graph coordinates into physical screen pixels,
    ensuring the entire graph is perfectly centered in the window.
    """
    # 1. Calculate the logical center of the graph
    logical_center_x = (min_x + max_x) / 2
    logical_center_y = (min_y + max_y) / 2

    # 2. Find the distance from the center and apply the scale
    offset_x = (logical_x - logical_center_x) * scale
    offset_y = (logical_y - logical_center_y) * scale

    # 3. Project this onto the physical center of the screen
    screen_x = (screen_width / 2) + offset_x
    screen_y = (screen_height / 2) + offset_y

    return screen_x, screen_y
