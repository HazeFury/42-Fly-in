from typing import Any

import arcade
from arcade.shape_list import ShapeElementList

from components.visual_hub import VisualHub
from core.graph import Network
from utils.get_path import get_complete_path
from utils.map_utils import (
    arcade_color_data,
    calculate_scale_factors,
    get_bounding_box,
    get_screen_coordinates,
)


class MapRenderer:
    """
    Handles all static visual elements of the map, including the background,
    connections (lines), hub circles, and labels. It also acts as the
    coordinate translator between logical space and screen space.
    """

    def __init__(
        self, graph_network: Network, window_width: int, window_height: int
    ) -> None:
        """Initializes the renderer and pre-builds the static GPU batches."""
        self.graph_network = graph_network
        self.window_width = window_width
        self.window_height = window_height

        # --- Map Scaling Initialization ---
        self.padding: int = 200

        self.min_x, self.max_x, self.min_y, self.max_y = get_bounding_box(
            self.graph_network.hubs
        )
        self.is_zoomed = True if self.max_x - self.min_x < 16 else False

        self.scale_x, self.scale_y = calculate_scale_factors(
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
            self.window_width,
            self.window_height,
            self.padding,
        )

        # --- Visual Containers ---
        self.background_texture = arcade.load_texture(
            get_complete_path("assets/map.png")
        )
        self.static_shapes = ShapeElementList()
        self.visual_hubs: list[VisualHub] = []
        self.hub_labels: list[arcade.Text] = []

        self.hub_color_data: dict[str, Any] = arcade_color_data

        # Build the static map immediately
        self._build_static_elements()

    def get_hub_position(self, hub_name: str) -> tuple[float, float]:
        """
        Translates a logical hub name into exact (x, y) screen coordinates.
        This allows external classes to move drones without doing math.
        """
        hub = self.graph_network.hubs[hub_name]
        return get_screen_coordinates(
            hub.x,
            hub.y,
            self.min_x,
            self.min_y,
            self.max_x,
            self.max_y,
            self.scale_x,
            self.scale_y,
            self.window_width,
            self.window_height,
        )

    def _build_static_elements(self) -> None:
        """Builds lines, hubs, and labels once into optimized containers."""

        # 1. Connection Lines
        for conn in self.graph_network.connections:
            x1, y1 = self.get_hub_position(conn.from_hub.name)
            x2, y2 = self.get_hub_position(conn.to_hub.name)

            line_shape = arcade.shape_list.create_line(
                start_x=x1,
                start_y=y1,
                end_x=x2,
                end_y=y2,
                color=arcade.color.GRAY,
                line_width=2.0,
            )
            self.static_shapes.append(line_shape)

        # 2. Hubs and Labels
        for hub in self.graph_network.hubs.values():
            screen_x, screen_y = self.get_hub_position(hub.name)

            # ---- Text Labels ----
            text_position = 30 if hub.x % 2 == 0 else -30
            if self.is_zoomed and text_position > 0:
                text_position = 45
            elif self.is_zoomed and text_position < 0:
                text_position = -45

            label = arcade.Text(
                font_name="Kenney Pixel",
                text=hub.name,
                x=screen_x,
                y=screen_y + text_position,
                color=arcade.color.WHITE,
                anchor_x="center",
                font_size=26 if self.is_zoomed else 16,
            )
            self.hub_labels.append(label)

            # ---- Hub Circles ----
            radius = 20 if self.is_zoomed else 12
            hub_color = (
                self.hub_color_data.get(hub.color, arcade.color.BLACK)
                if hub.color is not None
                else arcade.color.BLACK
            )

            v_hub = VisualHub(hub, screen_x, screen_y, radius, hub_color)
            self.visual_hubs.append(v_hub)

    def draw(self) -> None:
        """Renders the entire static background and map topology."""
        arcade.draw_texture_rect(
            texture=self.background_texture,
            rect=arcade.rect.XYWH(
                self.window_width / 2,
                self.window_height / 2,
                self.window_width,
                self.window_height,
            ),
        )
        self.static_shapes.draw()

        for v_hub in self.visual_hubs:
            v_hub.draw()

        for label in self.hub_labels:
            label.draw()
