from typing import Callable

import arcade
from arcade.gui import UIBoxLayout

from components.button import Button
from components.text import Text
from utils.get_path import get_complete_path


def create_end_level_dialog(
    turns: int, on_replay: Callable[[], None], on_exit: Callable[[], None]
) -> UIBoxLayout:
    """
    Constructs the end-of-level modal dialog with the final score
    and navigation buttons.

    Args:
        turns: The final tick count to display.
        on_replay: The function to execute when "Replay" is clicked.
        on_exit: The function to execute when "Exit" is clicked.
    """
    wood_path = get_complete_path("assets/wood_plank.png")
    bg_texture = arcade.load_texture(wood_path)

    content_box = UIBoxLayout(space_between=20)

    title_text = Text(
        text="LEVEL COMPLETED!", font_size=40, text_color=arcade.color.GREEN
    )
    content_box.add(title_text.with_padding(top=20, bottom=10))

    score_text = Text(
        text=f"Total Turns:   {turns}",
        font_size=24,
        text_color=arcade.color.BLACK,
    )
    content_box.add(score_text.with_padding(bottom=30))

    button_row = UIBoxLayout(vertical=False, space_between=30)

    button_row.add(
        Button(text="Replay", action=on_replay, width=150, height=50)
    )
    button_row.add(Button(text="Leave", action=on_exit, width=150, height=50))

    content_box.add(button_row.with_padding(bottom=20))

    styled_box = content_box.with_padding(
        top=50, bottom=50, left=150, right=150
    ).with_background(texture=bg_texture)

    return styled_box
