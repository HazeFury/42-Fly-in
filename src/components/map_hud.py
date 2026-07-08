from typing import Callable

import arcade
from arcade.gui import UIAnchorLayout, UIManager

from components.button import Button
from components.dialog import create_end_level_dialog


class MapHUD:
    """
    Manages all User Interface elements for the map view, including
    buttons, turn counter, and end-of-level dialogs.
    """

    def __init__(
        self,
        window: arcade.Window,
        on_toggle_mode: Callable[[], bool],
        on_exit: Callable[[], None],
        on_replay: Callable[[], None],
    ) -> None:
        """Initialize the HUD and its components."""
        self.window = window

        self.on_toggle_mode = on_toggle_mode
        self.on_exit = on_exit
        self.on_replay = on_replay

        self.manager = UIManager()
        self.ui_anchor = self.manager.add(UIAnchorLayout())

        self._setup_buttons()
        self._setup_turn_text()

    def _setup_buttons(self) -> None:
        """Creates and places the static UI buttons."""
        self.mode_button = Button(
            text="Mode: MANUEL",
            action=self._handle_mode_toggle,
            width=250,
            height=50,
        )
        self.ui_anchor.add(
            child=self.mode_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-20,
            align_y=-20,
        )

        exit_button = Button(
            text="exit",
            scale=0.8,
            action=self.on_exit,
            x=10,
            y=self.window.height - 50,
        )
        self.manager.add(exit_button)

    def _setup_turn_text(self) -> None:
        """Initializes the turn counter text object."""
        self.turn_text = arcade.Text(
            text="Turn: 0",
            x=self.window.width - 20,
            y=20,
            color=arcade.color.WHITE,
            font_size=28,
            font_name="Kenney Future",
            anchor_x="right",
            anchor_y="baseline",
        )

    def _handle_mode_toggle(self) -> None:
        """Callback triggered by the mode button. Updates its own text."""
        is_auto = self.on_toggle_mode()

        if is_auto:
            self.mode_button.text = "Mode: AUTO"
        else:
            self.mode_button.text = "Mode: MANUEL"

    def show_victory_dialog(self, final_tick: int) -> None:
        """Displays the end-of-level modal."""
        dialog = create_end_level_dialog(
            turns=final_tick,
            on_replay=self.on_replay,
            on_exit=self.on_exit,
        )
        self.ui_anchor.add(
            child=dialog, anchor_x="center_x", anchor_y="center_y"
        )

    def enable(self) -> None:
        """Enables UI interaction."""
        self.manager.enable()

    def disable(self) -> None:
        """Disables UI interaction."""
        self.manager.disable()

    def draw(self, current_tick: int) -> None:
        """Renders all HUD elements."""
        self.manager.draw()

        arcade.draw_rect_filled(
            rect=arcade.rect.XYWH(self.window.width - 115, 30, 230, 60),
            color=(0, 0, 0, 175),
        )

        self.turn_text.text = f"Turn: {current_tick}"
        self.turn_text.draw()
