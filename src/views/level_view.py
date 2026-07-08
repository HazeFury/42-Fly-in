import arcade
from arcade.gui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIManager,
)

from components.button import Button
from components.text import Text
from core.map_manager import maps_registry
from utils.get_path import get_complete_path
from utils.map_utils import verify_map
from utils.models import LevelData
from views.error_view import ErrorView
from views.map_view import MapView


class LevelView(arcade.View):
    """View for select the level."""

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
                level_data_opt = maps_registry.get_map(difficulty, level)

                if level_data_opt is not None:
                    valid_level_data: LevelData = level_data_opt

                    def launch_map(
                        current_data: LevelData = valid_level_data,
                    ) -> None:
                        is_valid = verify_map(current_data)

                        if is_valid:
                            self.window.show_view(MapView(current_data, self))
                        else:
                            self.window.show_view(ErrorView(self))

                    button_box.add(
                        Button(
                            text=level,
                            action=launch_map,
                            width=350,
                            height=100,
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

        global_box.add(
            Button(
                text="Go back",
                scale=1.5,
                action=lambda: self.window.show_view(DifficultyView()),
            )
        )

        anchor.add(global_box)

    def on_show_view(self) -> None:
        """Called by Arcade when this view is displayed on the screen."""
        self.ui.enable()

    def on_hide_view(self) -> None:
        """Called by Arcade when switching away from this view."""
        self.ui.disable()

    def on_draw(self) -> None:
        """Renders the view to the screen.
        Clears the window with a solid black background color."""
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
