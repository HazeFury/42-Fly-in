import arcade
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIManager,
)

from components.button import Button
from components.text import Text
from utils.get_path import get_complete_path
from views.difficulty_view import DifficultyView


class MenuView(arcade.View):
    """View for the menu."""

    def __init__(self) -> None:
        super().__init__()

        background_path = get_complete_path("assets/background.png")
        wood_plank = get_complete_path("assets/wood_plank.png")
        forty_two = get_complete_path("assets/42.png")

        self.background_texture = arcade.load_texture(background_path)
        self.wood_plank = arcade.load_texture(wood_plank)
        self.logo_texture = arcade.load_texture(":resources:/logo.png")
        self.forty_two = arcade.load_texture(forty_two)

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        button_box = UIBoxLayout(space_between=150)

        base_label = Text(
            text="Fly-in", font_size=100, text_color=arcade.color.BLACK
        )

        final_title_widget = base_label.with_padding(
            top=40, bottom=40, left=80, right=80
        ).with_background(texture=self.wood_plank)

        button_box.add(final_title_widget)

        button_box.add(
            Button(
                text="Play",
                action=lambda: self.window.show_view(DifficultyView()),
                scale=2.0,
            )
        )

        button_box.add(
            Button(text="Exit Game", action=lambda: self.window.close())
        )

        anchor.add(button_box)

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self) -> None:
        """
        Render the screen with the background and UI elements.
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

        arcade.draw_texture_rect(
            texture=self.logo_texture, rect=arcade.rect.XYWH(70, 70, 100, 100)
        )

        arcade.draw_texture_rect(
            texture=self.forty_two, rect=arcade.rect.XYWH(1850, 70, 100, 100)
        )

        self.ui.draw()
