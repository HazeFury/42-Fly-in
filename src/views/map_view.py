import arcade

from components.map_hud import MapHUD
from components.map_renderer import MapRenderer
from components.visual_drone import VisualDrone
from core.graph import Network
from core.simulation import SimulationEngine
from utils.get_path import get_complete_path
from utils.map_utils import get_drone_offset
from utils.models import LevelData

arcade.load_font(":resources:/fonts/ttf/Kenney/Kenney_Pixel.ttf")


class MapView(arcade.View):
    """View for displaying and managing the drone network simulation."""

    def __init__(
        self, level_data: LevelData, previous_view: arcade.View
    ) -> None:
        super().__init__()

        self.level_data = level_data
        self.previous_view = previous_view

        # 1. Logical Core
        self.graph_network = Network(level_data)
        self.engine = SimulationEngine(
            self.graph_network, level_data.nb_drones
        )

        # 2. Rendering Sub-Systems
        self.renderer = MapRenderer(
            self.graph_network, self.window.width, self.window.height
        )
        self.hud = MapHUD(
            window=self.window,
            on_toggle_mode=self._toggle_simulation_mode,
            on_exit=self._exit_to_previous_view,
            on_replay=self._replay_level,
        )

        # 3. Dynamic Elements (Drones)
        self.drone_list: arcade.SpriteList[VisualDrone] = arcade.SpriteList()
        self.visual_drones: dict[str, VisualDrone] = {}
        self._initialize_visual_drones()

        # 4. Simulation State
        self.is_auto = False
        self.time_since_last_tick = 0.0
        self.tick_rate = 1.0
        self.dialog_shown = False

    def _initialize_visual_drones(self) -> None:
        """Creates the visual drones and places them on the start hub."""
        drone_path = get_complete_path("assets/drone.png")

        for logical_drone in self.engine.drones:
            if logical_drone.current_hub is None:
                continue

            base_x, base_y = self.renderer.get_hub_position(
                logical_drone.current_hub
            )
            offset_x, offset_y = get_drone_offset(logical_drone.id)

            v_drone = VisualDrone(str(drone_path), scale=0.3)
            v_drone.center_x = base_x + offset_x
            v_drone.center_y = base_y + offset_y

            self.visual_drones[logical_drone.id] = v_drone
            self.drone_list.append(v_drone)

    def execute_tick(self) -> None:
        """Advances the simulation and animates drones."""
        if self.engine.is_finished:
            return

        old_positions = {
            d.id: (d.current_hub or d.transit_destination)
            for d in self.engine.drones
        }

        self.engine.next_tick()

        for logical_drone in self.engine.drones:
            new_logical_pos = (
                logical_drone.current_hub or logical_drone.transit_destination
            )

            if (
                new_logical_pos is not None
                and new_logical_pos != old_positions[logical_drone.id]
            ):
                base_target_x, base_target_y = self.renderer.get_hub_position(
                    new_logical_pos
                )
                offset_x, offset_y = get_drone_offset(logical_drone.id)

                anim_time = 1.0 if logical_drone.transit_destination else 0.5
                v_drone = self.visual_drones[logical_drone.id]

                v_drone.move_to(
                    target_x=base_target_x + offset_x,
                    target_y=base_target_y + offset_y,
                    travel_time=anim_time,
                )

    def _toggle_simulation_mode(self) -> bool:
        self.is_auto = not self.is_auto
        return self.is_auto

    def _exit_to_previous_view(self) -> None:
        self.window.show_view(self.previous_view)

    def _replay_level(self) -> None:
        self.window.show_view(MapView(self.level_data, self.previous_view))

    def on_show_view(self) -> None:
        self.hud.enable()

    def on_hide_view(self) -> None:
        self.hud.disable()

    def on_update(self, delta_time: float) -> None:
        """Called by Arcade 60 times per second to update the logic."""
        self.drone_list.update()
        self.drone_list.update_animation(delta_time)

        if self.engine.is_finished and not self.dialog_shown:
            self.dialog_shown = True
            self.is_auto = False
            self.hud.show_victory_dialog(self.engine.current_tick)

        if self.is_auto and not self.engine.is_finished:
            self.time_since_last_tick += delta_time
            if self.time_since_last_tick >= self.tick_rate:
                self.execute_tick()
                self.time_since_last_tick = 0.0

    def on_draw(self) -> None:
        """Render the screen strictly following the Painter's Algorithm."""
        self.clear(color=arcade.color.BLACK)

        self.renderer.draw()
        self.drone_list.draw()
        self.hud.draw(self.engine.current_tick)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handles keyboard input."""
        if symbol == arcade.key.SPACE and not self.is_auto:
            self.execute_tick()
