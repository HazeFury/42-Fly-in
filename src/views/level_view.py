import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
    UILabel
)
from components.button import Button
from components.text import Text
from utils.get_path import get_complete_path


class LevelView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self):
        super().__init__()

        background_path = get_complete_path("assets/background.png")
        self.background_texture = arcade.load_texture(background_path)

        levels = [
            {"level": "Easy"},
            {"level": "Medium"},
            {"level": "Hard"},
            {"level": "CHALLENGER"}
        ]

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        global_box = UIBoxLayout(space_between=200)
        button_box = UIBoxLayout(space_between=100, vertical=False)

        if levels:
            text = Text(text="Choose the difficulty")

            final_text = (
                text.with_padding(all=15)
                    .with_background(color=arcade.color.LIGHT_BROWN)
                    .with_border(color=arcade.color.BLACK, width=2)
                )

            for level in levels:
                button_box.add(Button(
                    text=level["level"],
                    action=lambda current=level["level"]: print(current),
                    width=200,
                    height=100
                    )
                )
            global_box.add(final_text)
            global_box.add(button_box)

        else:
            global_box.add(
                UILabel(
                    text="No level found !",
                    font_size=30,
                    text_color=arcade.color.WHITE,
                )
            )

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

    def on_draw(self):
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
