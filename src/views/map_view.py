import arcade
from typing import Any
from arcade.gui import UIManager
from components.button import Button
from components.visual_hub import VisualHub
from components.visual_drone import VisualDrone
from utils.get_path import get_complete_path
from utils.models import LevelData
from core.graph import Network
from utils.map_utils import arcade_color_data
from utils.map_utils import (
    get_bounding_box,
    calculate_scale_factors,
    get_screen_coordinates
)
arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Pixel.ttf")


class MapView(arcade.View):
    """View for displaying the drone network map."""

    def __init__(self, level_data: LevelData) -> None:
        super().__init__()

        # Instantiate the graph logic
        self.graph_network = Network(level_data)
        self.hub_labels: list[arcade.Text] = []
        self.visual_hubs: list[VisualHub] = []
        self.hub_color_data: dict[str, Any] = arcade_color_data

        # --- Map Scaling Initialization ---
        self.padding: int = 200

        # 1. Find the logical boundaries of the current map
        self.min_x, self.max_x, self.min_y, self.max_y = get_bounding_box(
            self.graph_network.hubs
        )
        self.is_zoomed = True if self.max_x - self.min_x < 16 else False
        # 2. Calculate the uniform scale factor once
        self.scale_x, self.scale_y = calculate_scale_factors(
            self.min_x, self.max_x,
            self.min_y, self.max_y,
            self.window.width, self.window.height,
            self.padding
        )

        # 1. Create a SpriteList to manage all drones efficiently
        self.drone_list = arcade.SpriteList()

        drone_path = get_complete_path("assets/drone.png")
        self.drone = VisualDrone(drone_path, scale=0.3)

        # Add our single drone to the list (for now)
        self.drone_list.append(self.drone)

        # 2. Place it on the starting hub
        self._place_drone_at_start()

        # --- Assets and UI ---
        background_path = get_complete_path("assets/map.png")
        self.background_texture = arcade.load_texture(background_path)

        from views.difficulty_view import DifficultyView

        self.ui = UIManager()
        self.ui.add(Button(
            text="exit",
            scale=0.8,
            action=lambda: self.window.show_view(DifficultyView()),
            x=10,
            y=self.window.height - 50
        ))
        self.setup()

    def setup(self) -> None:
        """Initialize labels using the non-uniform scale."""
        for hub in self.graph_network.hubs.values():
            screen_x, screen_y = get_screen_coordinates(
                hub.x, hub.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale_x, self.scale_y,
                self.window.width, self.window.height
            )

            # ---- Logic for text label ----
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
                font_size=26 if self.is_zoomed else 12
            )
            self.hub_labels.append(label)

            # ---- Logic for hub circle ----
            radius = 20 if self.is_zoomed else 12
            hub_color = (
                self.hub_color_data.get(hub.color, arcade.color.BLACK)
                if hub.color is not None
                else arcade.color.BLACK
            )

            v_hub = VisualHub(hub, screen_x, screen_y, radius, hub_color)
            self.visual_hubs.append(v_hub)

    def _place_drone_at_start(self) -> None:
        """
        Finds the start_hub in the parsed data and teleports the drone
        to its exact screen coordinates.
        """
        # Find the starting hub logic object
        start_hub = next(
            hub for hub in self.graph_network.hubs.values() if
            hub.zone_type == "start_hub"
        )

        screen_x, screen_y = get_screen_coordinates(
            start_hub.x, start_hub.y,
            self.min_x, self.min_y, self.max_x, self.max_y,
            self.scale_x, self.scale_y,
            self.window.width, self.window.height
        )

        self.drone.center_x = screen_x
        self.drone.center_y = screen_y

    def on_update(self, delta_time: float) -> None:
        """
        Called 60 times per second to update game logic.
        """
        # 3. Feed the real time (delta_time) to the drone's internal timer
        self.drone_list.update(delta_time)

    def on_show_view(self) -> None:
        """Called when the view is shown."""
        self.ui.enable()

    def on_hide_view(self) -> None:
        """Called when the view is hidden."""
        self.ui.disable()

    def on_draw(self) -> None:
        """Render the screen following the Painter's Algorithm."""
        self.clear(color=arcade.color.BLACK)

        # 1. Draw the background
        arcade.draw_texture_rect(
            texture=self.background_texture,
            rect=arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height
            )
        )

        # 2. Draw Connections (behind the hubs)
        for connection in self.graph_network.connections:
            # Pass both self.scale_x and self.scale_y
            x1, y1 = get_screen_coordinates(
                connection.hub_a.x, connection.hub_a.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale_x, self.scale_y,
                self.window.width, self.window.height
            )
            x2, y2 = get_screen_coordinates(
                connection.hub_b.x, connection.hub_b.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale_x, self.scale_y,
                self.window.width, self.window.height
            )

            # Draw the line
            arcade.draw_line(x1, y1, x2, y2, arcade.color.BLACK, line_width=2)

        # 3. Draw Hubs (on top of connections)
        for v_hub in self.visual_hubs:
            v_hub.draw()

        # 4. Draw hub details (name, max_drones)
            for label in self.hub_labels:
                label.draw()

        # 5. Draw the drone LAST so it appears ON TOP of the hubs and lines
        self.drone_list.draw()

        # 6. Draw UI elements (buttons)
        self.ui.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        Temporary debug input to test the Lerp movement.
        """
        if symbol == arcade.key.SPACE:
            end_hub = next(
                hub for hub in self.graph_network.hubs.values() if
                hub.zone_type == "end_hub"
            )

            target_x, target_y = get_screen_coordinates(
                end_hub.x, end_hub.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale_x, self.scale_y,
                self.window.width, self.window.height
            )

            self.drone.move_to(target_x, target_y, travel_time=2.0)
