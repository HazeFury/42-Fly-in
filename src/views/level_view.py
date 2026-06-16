import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
    UILabel
)
from ui.button import Button


class LevelView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self):
        super().__init__()

        levels = [
            {"level": "Easy"},
            {"level": "Medium"},
            {"level": "Hard"},
            {"level": "CHALLENGER"}
        ]

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        global_box = UIBoxLayout(space_between=80)
        button_box = UIBoxLayout(space_between=100, vertical=False)

        if levels:
            global_box.add(
                UILabel(
                    text="Choose the difficulty",
                    font_size=30,
                    text_color=arcade.color.WHITE,
                )
            )

            for level in levels:
                button_box.add(Button(
                    text=level["level"],
                    action=lambda current=level["level"]: print(current),
                    width=200,
                    height=100
                    )
                )
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
            action=lambda: self.window.show_view(MenuView())
            )
        )

        anchor.add(global_box)

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self):
        self.clear(color=arcade.uicolor.GREEN_EMERALD)

        self.ui.draw()
