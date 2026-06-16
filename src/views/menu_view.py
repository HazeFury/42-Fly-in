import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
)
from views.level_view import LevelView
from components.button import Button
from components.text import Text


class MenuView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self):
        super().__init__()

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        button_box = UIBoxLayout(space_between=100)

        button_box.add(
            Text(
                text="Fly-in",
                font_size=80,
                font_name="Kenney Blocks",
            )
        )

        button_box.add(Button(
            text="Play",
            action=lambda: self.window.show_view(LevelView())
            )
        )

        button_box.add(Button(
            text="Exit Game",
            action=lambda: self.window.close()
            )
        )

        anchor.add(button_box)

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self):
        self.clear(color=arcade.uicolor.GREEN_EMERALD)

        self.ui.draw()
