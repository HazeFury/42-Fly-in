import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
)
from src.components.button import Button
from src.components.text import Text
from src.utils.get_path import get_complete_path
from src.views.level_view import LevelView


class DifficultyView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self) -> None:
        super().__init__()

        background_path = get_complete_path("assets/background.png")
        self.background_texture = arcade.load_texture(background_path)

        difficulties = [
            "easy",
            "medium",
            "hard",
            "challenger"
        ]

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        global_box = UIBoxLayout(space_between=200)
        button_box = UIBoxLayout(space_between=100, vertical=False)

        text = Text(text="Choose the difficulty")

        final_text = (
            text.with_padding(all=15)
                .with_background(color=arcade.color.LIGHT_BROWN)
                .with_border(color=arcade.color.BLACK, width=2)
            )

        for diff in difficulties:
            button_box.add(Button(
                text=diff,
                action=lambda choosen_diff=diff: self.window.show_view(
                    LevelView(choosen_diff)
                    ),
                width=200,
                height=100
                )
            )
        global_box.add(final_text)
        global_box.add(button_box)

        from views.menu_view import MenuView

        global_box.add(Button(
            text="Go back to menu",
            scale=1.5,
            action=lambda: self.window.show_view(MenuView())
            )
        )

        anchor.add(global_box)

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self) -> None:
        self.clear(color=arcade.color.BLACK)

        arcade.draw_texture_rect(
            texture=self.background_texture,
            rect=arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height
            )
        )

        self.ui.draw()
