import arcade
from arcade.gui import UIManager
from components.button import Button
from utils.get_path import get_complete_path
from utils.models import LevelData
from core.graph import Network
from utils.map_utils import (
    get_bounding_box,
    calculate_scale_factor,
    get_screen_coordinates
)
arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Pixel.ttf")


class MapView(arcade.View):
    """View for displaying the drone network map."""

    def __init__(self, level_data: LevelData) -> None:
        super().__init__()

        # Instantiate the graph logic
        self.graph_network = Network(level_data)

        # --- Map Scaling Initialization ---
        self.padding: int = 200

        # 1. Find the logical boundaries of the current map
        self.min_x, self.max_x, self.min_y, self.max_y = get_bounding_box(
            self.graph_network.hubs
        )

        # 2. Calculate the uniform scale factor once
        # Using the constant 1680x1050 defined in your main.py
        self.scale: float = calculate_scale_factor(
            self.min_x, self.max_x,
            self.min_y, self.max_y,
            1920, 1080,
            self.padding
        )

        self.hub_labels: list[arcade.Text] = []

        self.hub_color_data = {
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
        # self.load_custom_fonts()
        self.setup()

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

    def setup(self) -> None:
        for hub in self.graph_network.hubs.values():
            screen_x, screen_y = get_screen_coordinates(
                hub.x, hub.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale, self.window.width, self.window.height
            )

            text_position = 30 if hub.x % 2 == 0 else -30

            label = arcade.Text(
                font_name="Kenney Pixel",
                text=hub.name,
                x=screen_x,
                y=screen_y + text_position,
                color=arcade.color.WHITE,
                anchor_x="center",
            )
            self.hub_labels.append(label)

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
            x1, y1 = get_screen_coordinates(
                connection.hub_a.x, connection.hub_a.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale, self.window.width, self.window.height
            )
            x2, y2 = get_screen_coordinates(
                connection.hub_b.x, connection.hub_b.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale, self.window.width, self.window.height
            )

            # TODO: Customize line thickness/color based on connection.capacity
            arcade.draw_line(x1, y1, x2, y2, arcade.color.WHITE, line_width=2)

        # 3. Draw Hubs (on top of connections)
        for hub in self.graph_network.hubs.values():
            screen_x, screen_y = get_screen_coordinates(
                hub.x, hub.y,
                self.min_x, self.min_y, self.max_x, self.max_y,
                self.scale, self.window.width, self.window.height
            )

            # TODO: Customize circle color based on hub.color or hub.zone_type
            arcade.draw_circle_filled(
                screen_x, screen_y, 10, self.hub_color_data.get(
                    hub.color, arcade.color.BLACK
                    )
                )

            # TODO: Draw hub details (name, max_drones)
            for label in self.hub_labels:
                label.draw()

        # 4. Draw UI elements (buttons)
        self.ui.draw()
