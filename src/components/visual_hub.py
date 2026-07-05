from typing import Any

import arcade

from core.graph import Hub
from utils.get_path import get_complete_path

# Preload textures at the module level so they are loaded into RAM only once!
TEX_BLOCKED = arcade.load_texture(get_complete_path("assets/icons/skull.png"))
TEX_END = arcade.load_texture(get_complete_path("assets/icons/end_flag.png"))
TEX_PRIORITY = arcade.load_texture(
    get_complete_path("assets/icons/battery.png")
)
TEX_RESTRICTED = arcade.load_texture(
    get_complete_path("assets/icons/warning.png")
)


class VisualHub:
    """
    Visual component responsible for rendering a hub circle and its inner icon.
    """

    def __init__(
        self,
        hub_data: Hub,
        screen_x: float,
        screen_y: float,
        radius: float,
        color: Any,
    ) -> None:
        """
        Initialize the visual hub and setup its icon if necessary.
        """
        self.hub_data = hub_data
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.radius = radius
        self.color = color
        self.icon_texture: arcade.Texture | None = None
        self.icon_width: float = 0
        self.icon_height: float = 0

        self._setup_icon()

    def _setup_icon(self) -> None:
        """Assigns the correct texture based on the zone type or access."""
        texture = None

        if self.hub_data.zone_type == "end_hub":
            texture = TEX_END
        elif self.hub_data.access == "priority":
            texture = TEX_PRIORITY
        elif self.hub_data.access == "blocked" or "dead" in self.hub_data.name:
            texture = TEX_BLOCKED
        elif self.hub_data.access == "restricted":
            texture = TEX_RESTRICTED

        if texture:
            self.icon_texture = texture

            # Scale the icon to fit nicely inside the circle
            max_dim = max(texture.width, texture.height)
            scale = (self.radius * 1.2) / max_dim

            self.icon_width = texture.width * scale
            self.icon_height = texture.height * scale

    def draw(self) -> None:
        """Renders the hub circle and its icon if it exists."""
        arcade.draw_circle_filled(
            self.screen_x, self.screen_y, self.radius, self.color
        )

        if self.icon_texture:
            arcade.draw_texture_rect(
                texture=self.icon_texture,
                rect=arcade.rect.XYWH(
                    self.screen_x,
                    self.screen_y,
                    self.icon_width,
                    self.icon_height,
                ),
            )
