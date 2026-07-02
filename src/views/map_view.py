import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
)
from components.button import Button
from utils.get_path import get_complete_path
from utils.models import LevelData
from core.graph import Network
from utils.map_utils import (
    get_bounding_box,
    calculate_scale_factor,
    get_screen_coordinates
)


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
            1680, 1050,
            self.padding
        )

        # --- Assets and UI ---
        background_path = get_complete_path("assets/map.png")
        self.background_texture = arcade.load_texture(background_path)

        self.ui = UIManager()
        # anchor = self.ui.add(UIAnchorLayout())
        # global_box = UIBoxLayout(space_between=200)

        # from views.menu_view import MenuView

        # global_box.add(Button(
        #     text="Go back to menu",
        #     scale=1.5,
        #     action=lambda: self.window.show_view(MenuView())
        # ))

        # anchor.add(global_box)

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
                screen_x, screen_y, 25, arcade.color.ARSENIC
                )

            # TODO: Draw hub details (name, max_drones)
            arcade.draw_text(
                hub.name,
                screen_x,
                screen_y + 30,
                arcade.color.WHITE,
                anchor_x="center",
                font_size=12
            )

        # 4. Draw UI elements (buttons)
        self.ui.draw()
