import arcade
from arcade.gui import (
    UIManager,
    UIAnchorLayout,
    UIBoxLayout,
)
from components.button import Button
from utils.get_path import get_complete_path
from utils.models import LevelData
from core.graph import Network


class MapView(arcade.View):
    """View for displaying the map."""

    def __init__(self, level_data: LevelData) -> None:
        super().__init__()

        graph_network = Network(level_data)

        print(graph_network.hubs)

        background_path = get_complete_path("assets/background.png")
        self.background_texture = arcade.load_texture(background_path)

        self.ui = UIManager()
        anchor = self.ui.add(UIAnchorLayout())
        global_box = UIBoxLayout(space_between=200)

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
