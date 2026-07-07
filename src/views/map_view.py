from typing import Any

import arcade
from arcade.gui import UIAnchorLayout, UIManager
from arcade.shape_list import ShapeElementList

from components.button import Button
from components.dialog import create_end_level_dialog
from components.visual_drone import VisualDrone
from components.visual_hub import VisualHub
from core.graph import Network
from core.simulation import SimulationEngine
from utils.get_path import get_complete_path
from utils.map_utils import (
    arcade_color_data,
    calculate_scale_factors,
    get_bounding_box,
    get_drone_offset,
    get_screen_coordinates,
)
from utils.models import LevelData

arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Pixel.ttf")


class MapView(arcade.View):
    """View for displaying the drone network map."""

    def __init__(
        self, level_data: LevelData, previous_view: arcade.View
    ) -> None:
        super().__init__()

        # Instantiate the graph logic
        self.level_data = level_data
        self.graph_network = Network(level_data)
        self.engine = SimulationEngine(
            self.graph_network, level_data.nb_drones
        )
        # 1. Vector graphics batch (Lines)
        self.visual_conn: ShapeElementList[Any] = ShapeElementList()

        # 2. Custom visual components
        self.visual_hubs: list[VisualHub] = []

        # 3. Pre-instantiated texts
        self.hub_labels: list[arcade.Text] = []
        self.hub_color_data: dict[str, Any] = arcade_color_data
        self.dialog_shown = False
        self.previous_view = previous_view

        # --- Map Scaling Initialization ---
        self.padding: int = 200

        # 1. Find the logical boundaries of the current map
        self.min_x, self.max_x, self.min_y, self.max_y = get_bounding_box(
            self.graph_network.hubs
        )
        self.is_zoomed = True if self.max_x - self.min_x < 16 else False
        # 2. Calculate the uniform scale factor once
        self.scale_x, self.scale_y = calculate_scale_factors(
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
            self.window.width,
            self.window.height,
            self.padding,
        )

        # 1. Create a SpriteList to manage all drones efficiently
        self.drone_list: arcade.SpriteList[VisualDrone] = arcade.SpriteList()
        # Dictionary linking logical drone ID ("D1") to its visual sprite
        self.visual_drones: dict[str, VisualDrone] = {}

        for logical_drone in self.engine.drones:
            if logical_drone.current_hub is None:
                continue

            start_hub = self.graph_network.hubs[logical_drone.current_hub]
            base_x, base_y = get_screen_coordinates(
                start_hub.x,
                start_hub.y,
                self.min_x,
                self.min_y,
                self.max_x,
                self.max_y,
                self.scale_x,
                self.scale_y,
                self.window.width,
                self.window.height,
            )

            # 2. Get the unique offset for this specific drone
            offset_x, offset_y = get_drone_offset(logical_drone.id)
            drone_path = get_complete_path("assets/drone.png")
            v_drone = VisualDrone(str(drone_path), scale=0.3)
            v_drone.center_x = base_x + offset_x
            v_drone.center_y = base_y + offset_y
            self.visual_drones[logical_drone.id] = v_drone
            self.drone_list.append(v_drone)

        # 3. Teleport everyone to the starting line
        self._place_drones_at_start()

        # --- Auto/Manual System ---
        self.is_auto = False
        self.time_since_last_tick = 0.0
        self.tick_rate = 1.0  # Time in seconds between each automatic tick

        # Setup the UI Manager for the MapView
        self.manager = UIManager()
        anchor = self.manager.add(UIAnchorLayout())

        self.mode_button = Button(
            text="Mode: MANUEL", action=self.toggle_mode, width=250, height=50
        )

        # Arcade 3.0 syntax: anchor properties are passed directly to the
        # layout's add method
        anchor.add(
            child=self.mode_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-20,
            align_y=-20,
        )

        # --- Assets and UI ---
        background_path = get_complete_path("assets/map.png")
        self.background_texture = arcade.load_texture(background_path)

        self.ui = UIManager()

        from views.difficulty_view import DifficultyView

        self.ui.add(
            Button(
                text="exit",
                scale=0.8,
                action=lambda: self.window.show_view(DifficultyView()),
                x=10,
                y=self.window.height - 50,
            )
        )

        self.turn_text = arcade.Text(
            text=f"Turn: {self.engine.current_tick}",
            x=self.window.width - 20,
            y=20,
            color=arcade.color.WHITE,
            font_size=28,
            font_name="Kenney Future",
            anchor_x="right",
            anchor_y="baseline",
        )

        # Remplacer 'anchor =' par 'self.ui_anchor ='
        self.ui_anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        # Et on utilise self.ui_anchor pour le bouton
        self.ui_anchor.add(
            child=self.mode_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-20,
            align_y=-20,
        )

        self.setup()

    def setup(self) -> None:
        """
        Pre-computes and sorts static map elements into optimized
        containers (shapes, sprites, and texts) for fast rendering.
        """
        # ---- Logic for Connection lines (Vector Graphics) ----
        for conn in self.graph_network.connections:
            start_hub = self.graph_network.hubs[conn.from_hub.name]
            end_hub = self.graph_network.hubs[conn.to_hub.name]

            x1, y1 = get_screen_coordinates(
                start_hub.x,
                start_hub.y,
                self.min_x,
                self.min_y,
                self.max_x,
                self.max_y,
                self.scale_x,
                self.scale_y,
                self.window.width,
                self.window.height,
            )
            x2, y2 = get_screen_coordinates(
                end_hub.x,
                end_hub.y,
                self.min_x,
                self.min_y,
                self.max_x,
                self.max_y,
                self.scale_x,
                self.scale_y,
                self.window.width,
                self.window.height,
            )

            # Valid for ShapeElementList
            line_shape = arcade.shape_list.create_line(
                start_x=x1,
                start_y=y1,
                end_x=x2,
                end_y=y2,
                color=arcade.color.GRAY,
                line_width=2.0,
            )
            self.visual_conn.append(line_shape)

        # ---- Logic for Hubs (Sprites) and Labels (Text) ----
        for hub in self.graph_network.hubs.values():
            screen_x, screen_y = get_screen_coordinates(
                hub.x,
                hub.y,
                self.min_x,
                self.min_y,
                self.max_x,
                self.max_y,
                self.scale_x,
                self.scale_y,
                self.window.width,
                self.window.height,
            )

            # ---- Text Labels ----
            text_position = 30 if hub.x % 2 == 0 else -30
            if self.is_zoomed and text_position > 0:
                text_position = 45
            elif self.is_zoomed and text_position < 0:
                text_position = -45

            # Instantiate once and keep in a standard list
            label = arcade.Text(
                font_name="Kenney Pixel",
                text=hub.name,
                x=screen_x,
                y=screen_y + text_position,
                color=arcade.color.WHITE,
                anchor_x="center",
                font_size=26 if self.is_zoomed else 16,
            )
            self.hub_labels.append(label)

            # ---- Hub Circles ----
            radius = 20 if self.is_zoomed else 12
            hub_color = (
                self.hub_color_data.get(hub.color, arcade.color.BLACK)
                if hub.color is not None
                else arcade.color.BLACK
            )

            v_hub = VisualHub(hub, screen_x, screen_y, radius, hub_color)
            self.visual_hubs.append(v_hub)

    def _place_drones_at_start(self) -> None:
        """
        Teleports all visual drones to the starting hub's screen coordinates.
        """
        start_hub_name, _ = self.graph_network.get_start_and_exit_hub()
        start_hub = self.graph_network.hubs[start_hub_name]

        screen_x, screen_y = get_screen_coordinates(
            start_hub.x,
            start_hub.y,
            self.min_x,
            self.min_y,
            self.max_x,
            self.max_y,
            self.scale_x,
            self.scale_y,
            self.window.width,
            self.window.height,
        )

        for v_drone in self.visual_drones.values():
            v_drone.center_x = screen_x
            v_drone.center_y = screen_y

    def toggle_mode(self) -> None:
        """Switches between Auto and Manual simulation modes."""
        self.is_auto = not self.is_auto

        if self.is_auto:
            self.mode_button.text = "Mode: AUTO"
        else:
            self.mode_button.text = "Mode: MANUEL"

    def on_update(self, delta_time: float) -> None:
        """Called by Arcade 60 times per second to update the logic."""
        self.drone_list.update()
        self.drone_list.update_animation(delta_time)

        # Check for victory condition
        if self.engine.is_finished and not self.dialog_shown:
            self.dialog_shown = True
            self.is_auto = (
                False  # Ensure auto-mode stops pressing the gas pedal
            )
            self._show_victory_dialog()

        if self.is_auto and not self.engine.is_finished:
            self.time_since_last_tick += delta_time

            if self.time_since_last_tick >= self.tick_rate:
                self.execute_tick()
                self.time_since_last_tick = 0.0

    def _show_victory_dialog(self) -> None:
        def trigger_replay() -> None:
            self.window.show_view(MapView(self.level_data, self.previous_view))

        def trigger_exit() -> None:

            self.window.show_view(self.previous_view)

        dialog = create_end_level_dialog(
            turns=self.engine.current_tick,
            on_replay=trigger_replay,
            on_exit=trigger_exit,
        )

        # Le secret est ici : on l'ajoute à self.ui_anchor, pas à self.manager
        self.ui_anchor.add(
            child=dialog, anchor_x="center_x", anchor_y="center_y"
        )

    def on_show_view(self) -> None:
        """Called when the view is shown."""
        self.ui.enable()
        self.manager.enable()

    def on_hide_view(self) -> None:
        """Called when the view is hidden."""
        self.ui.disable()
        self.manager.disable()

    def on_draw(self) -> None:
        """Render the screen following the Painter's Algorithm."""
        self.clear(color=arcade.color.BLACK)

        # 1. Draw the background
        arcade.draw_texture_rect(
            texture=self.background_texture,
            rect=arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height,
            ),
        )

        # 2. Vector Lines (One big batched GPU call)
        self.visual_conn.draw()

        # 3. Hubs (Custom draw calls)
        for v_hub in self.visual_hubs:
            v_hub.draw()

        for label in self.hub_labels:
            label.draw()
        # 5. Draw the drone LAST so it appears ON TOP of the hubs and lines
        self.drone_list.draw()

        # 6. Draw UI elements (buttons)
        self.ui.draw()
        self.manager.draw()

        # background for tick counter
        arcade.draw_rect_filled(
            rect=arcade.rect.XYWH(
                self.window.width - 115,  # center_x (width - la moitié de 220)
                30,  # center_y (la moitié de 80)
                230,  # width
                60,  # height
            ),
            color=(0, 0, 0, 175),
        )

        # Draw the HUD last so it is always on top
        self.turn_text.draw()

    def execute_tick(self) -> None:
        """
        Executes a single turn of the simulation, updates the HUD,
        and triggers the visual drone animations.
        """
        if self.engine.is_finished:
            return

        # 1. Snapshot logical position BEFORE the tick
        old_positions = {
            d.id: (d.current_hub or d.transit_destination)
            for d in self.engine.drones
        }

        # 2. Advance the engine
        self.engine.next_tick()

        # Update the HUD
        self.turn_text.text = f"Turn: {self.engine.current_tick}"

        # 3. Compare new positions and animate
        for logical_drone in self.engine.drones:
            new_logical_pos = (
                logical_drone.current_hub or logical_drone.transit_destination
            )

            if (
                new_logical_pos is not None
                and new_logical_pos != old_positions[logical_drone.id]
            ):
                dest_hub = self.graph_network.hubs[new_logical_pos]
                base_target_x, base_target_y = get_screen_coordinates(
                    dest_hub.x,
                    dest_hub.y,
                    self.min_x,
                    self.min_y,
                    self.max_x,
                    self.max_y,
                    self.scale_x,
                    self.scale_y,
                    self.window.width,
                    self.window.height,
                )
                offset_x, offset_y = get_drone_offset(logical_drone.id)

                anim_time = 1.0 if logical_drone.transit_destination else 0.5
                v_drone = self.visual_drones[logical_drone.id]
                v_drone.move_to(
                    target_x=base_target_x + offset_x,
                    target_y=base_target_y + offset_y,
                    travel_time=anim_time,
                )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handles keyboard input."""
        # Spacebar only works if we are NOT in auto mode
        if symbol == arcade.key.SPACE and not self.is_auto:
            self.execute_tick()
