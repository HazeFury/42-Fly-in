import arcade
from arcade.gui import UILabel

arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Blocks.ttf")
arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Mini_Square.ttf")


class Text(UILabel):
    """
    Custom UI Button standardizing the visual styling across the application.
    """

    def __init__(self,
                 text: str,
                 font_size: int = 30,
                 text_color=arcade.color.WHITE,
                 font_name="Kenney Mini Square",
                 **kwargs):
        """
        Initialize the custom button with predefined textures.
        """
        # Call the parent class constructor without using 'return'
        super().__init__(
            text=text,
            font_size=font_size,
            text_color=text_color,
            font_name=font_name,
            **kwargs
            )
