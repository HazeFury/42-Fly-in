import arcade
from arcade.gui import UITextureButton
from typing import Callable, Any

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


class Button(UITextureButton):
    """
    Custom UI Button standardizing the visual styling across the application.
    """

    def __init__(self, text: str, action: Callable[..., Any], **kwargs):
        """
        Initialize the custom button with predefined textures.
        """
        # Call the parent class constructor without using 'return'
        super().__init__(
            text=text,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
            **kwargs)

        @self.event("on_click")
        def on_click(event):
            action()
