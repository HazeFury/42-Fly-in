import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
    UILabel
)
from views.level_view import LevelView
from ui.button import Button

arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Blocks.ttf")


class MenuView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self):
        super().__init__()

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        button_box = UIBoxLayout(space_between=100)

        button_box.add(
            UILabel(
                text="Snake Game",
                font_size=50,
                text_color=arcade.color.WHITE,
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
