import arcade
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIAnchorLayout,
    UIBoxLayout,
    UILabel
)
# from views.level_selection import LevelView

# Preload textures, because they are mostly used multiple times,so they are not
# loaded multiple times
TEX_RED_BUTTON_NORMAL = arcade.load_texture(
    ":resources:gui_basic_assets/button/red_normal.png"
)
TEX_RED_BUTTON_HOVER = arcade.load_texture(
    ":resources:gui_basic_assets/button/red_hover.png"
)
TEX_RED_BUTTON_PRESS = arcade.load_texture(
    ":resources:gui_basic_assets/button/red_press.png"
)
arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Blocks.ttf")


class MenuView(arcade.View):
    """Uses the arcade.View and shows how to integrate UIManager."""

    def __init__(self):
        super().__init__()

        # Create a UIManager
        self.ui = UIManager()

        # Create anchor layout, which can be used to position widgets on screen
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

        # Add a button switch to the other View.
        play_button = button_box.add(
            UITextureButton(
                text="Play",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS,
            )
        )

        @play_button.event("on_click")
        def on_click_play(event):
            # self.window.show_view(LevelView())
            print("go to level view")

        exit_button = button_box.add(
            UITextureButton(
                text="Exit Game",
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS,
            )
        )

        @exit_button.event("on_click")
        def on_click_exit(event):
            self.window.close()

        anchor.add(button_box)

    def on_show_view(self) -> None:
        self.ui.enable()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def on_draw(self):
        # Clear the screen
        self.clear(color=arcade.uicolor.GREEN_EMERALD)

        # Add draw commands that should be below the UI
        # ...

        self.ui.draw()

        # Add draw commands that should be on top of the UI (uncommon)
        # ...
