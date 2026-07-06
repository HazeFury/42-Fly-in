import arcade
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIManager,
)

from components.button import Button
from components.text import Text
from utils.get_path import get_complete_path


class ErrorView(arcade.View):
    """View displayed when a selected map is unsolvable."""

    def __init__(self, previous_view: arcade.View) -> None:
        super().__init__()
        self.previous_view = previous_view

        background_path = get_complete_path("assets/night_bg.png")
        wood_plank = get_complete_path("assets/wood_plank.png")

        self.background_texture = arcade.load_texture(background_path)
        self.wood_plank = arcade.load_texture(wood_plank)

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())

        content_box = UIBoxLayout(space_between=40)

        base_label = Text(
            text="Unsolvable Map!", font_size=60, text_color=arcade.color.RED
        )

        title_widget = base_label.with_padding(
            top=30, bottom=30, left=60, right=60
        ).with_background(texture=self.wood_plank)

        content_box.add(title_widget)

        subtitle = Text(
            text="There is no valid path from the start to the goal.",
            font_size=24,
            text_color=arcade.color.WHITE,
        )
        content_box.add(subtitle)

        content_box.add(
            Button(text="Back to Levels", action=self.go_back, scale=1.5)
        )

        anchor.add(content_box)

    def go_back(self) -> None:
        """Returns to the previous level selection screen."""
        self.window.show_view(self.previous_view)

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self) -> None:
        """
        Render the screen with the background, logos, and UI elements.
        """
        self.clear(color=arcade.color.BLACK)

        arcade.draw_texture_rect(
            texture=self.background_texture,
            rect=arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height,
            ),
        )
        self.ui.draw()
