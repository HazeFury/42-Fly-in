import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
)
from src.components.button import Button
from src.components.text import Text
from src.utils.get_path import get_complete_path
from src.core.map_manager import maps_registry


class LevelView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self, difficulty: str) -> None:
        super().__init__()

        background_path = get_complete_path("assets/background.png")
        self.background_texture = arcade.load_texture(background_path)

        raw_levels = maps_registry.get_maps_by_difficulty(difficulty)
        levels = [level_name for level_name in raw_levels.keys()]

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        global_box = UIBoxLayout(space_between=200)
        button_box = UIBoxLayout(space_between=100, vertical=False)

        if levels:
            text = Text(text="Choose the level")

            final_text = (
                text.with_padding(all=15)
                    .with_background(color=arcade.color.LIGHT_BROWN)
                    .with_border(color=arcade.color.BLACK, width=2)
                )

            for level in levels:
                button_box.add(Button(
                    text=level,
                    action=lambda current=level: print(current),
                    width=350,
                    height=100
                    )
                )
            global_box.add(final_text)
            global_box.add(button_box)

        else:
            not_found_text = Text(text="No level found !")
            global_box.add(
                not_found_text.with_padding(all=15)
                .with_background(color=arcade.color.BLACK)
                .with_border(color=arcade.color.BLACK, width=2)
            )

        from views.difficulty_view import DifficultyView

        global_box.add(Button(
            text="Go back",
            scale=1.5,
            action=lambda: self.window.show_view(DifficultyView())
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
