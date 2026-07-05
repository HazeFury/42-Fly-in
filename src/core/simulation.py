from typing import Any, List

from core.pathfinding import calculate_dijkstra_path
from utils.logger import logger


class LogicalDrone:
    """
    Represents the logical state of a drone in the network.
    It knows its ID, its planned route, and its current progress.
    """

    def __init__(
        self, drone_id: str, start_hub: str, optimal_path: List[str]
    ) -> None:
        self.id = drone_id
        self.current_hub = start_hub
        self.path = optimal_path
        self.path_index = 0
        self.is_delivered = False

    def get_next_hub(self) -> str | None:
        """Returns the next destination on the path, or None if finished."""
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None

    def move_forward(self) -> str | None:
        """
        Advances the drone to the next hub and updates its state.
        Returns the destination name if it moved, or None.
        """
        if self.is_delivered:
            return None

        next_hub = self.get_next_hub()
        if next_hub:
            self.path_index += 1
            self.current_hub = next_hub

            # Check if we reached the final destination
            if self.path_index == len(self.path) - 1:
                self.is_delivered = True

            return next_hub

        return None


class SimulationEngine:
    """
    The main orchestrator. Advances time (ticks) and coordinates
    the movement of all drones according to the rules.
    """

    def __init__(self, graph_network: Any, nb_drones: int) -> None:
        self.graph = graph_network
        self.drones: List[LogicalDrone] = []
        self.current_tick = 0
        self.is_finished = False

        self._initialize_drones(nb_drones)

    def _initialize_drones(self, nb_drones: int) -> None:
        """
        Creates all drones, calculates their optimal paths, and sets them
        at the start.
        """
        start_hub, end_hub = self.graph.get_start_and_exit_hub()

        # Calculate the golden path once (since all drones share the same goal
        # for now)
        optimal_path = calculate_dijkstra_path(self.graph, start_hub, end_hub)

        if not optimal_path:
            logger.critical(
                "Cannot initialize simulation: No valid path exists!"
            )
            return

        logger.debug(f"Calculated optimal path: {' -> '.join(optimal_path)}")

        for i in range(nb_drones):
            # Drone IDs as requested by the subject: D1, D2, D3...
            drone_id = f"D{i + 1}"
            new_drone = LogicalDrone(drone_id, start_hub, optimal_path)
            self.drones.append(new_drone)

    def next_tick(self) -> None:
        """
        Resolves one turn of the simulation.
        Checks for hub capacities and connection limits before moving.
        """
        if self.is_finished:
            return

        self.current_tick += 1
        movements_this_turn: List[str] = []

        # 1. Take a snapshot of the current hub occupancy
        hub_occupancy = {hub_name: 0 for hub_name in self.graph.hubs.keys()}
        for drone in self.drones:
            if not drone.is_delivered:
                hub_occupancy[drone.current_hub] += 1

        # Track how much bandwidth each connection has used THIS specific turn
        link_usage: dict[tuple[str, str], int] = {}

        def get_link_capacity(hub_a: str, hub_b: str) -> int:
            """Helper to find the connection capacity between two hubs."""
            for conn in self.graph.connections:
                if (
                    conn.from_hub.name == hub_a and conn.to_hub.name == hub_b
                ) or (
                    conn.from_hub.name == hub_b and conn.to_hub.name == hub_a
                ):
                    return conn.capacity
            return 1  # Fallback

        # 2. Process each drone sequentially (D1 acts before D2, etc.)
        for drone in self.drones:
            if drone.is_delivered:
                continue

            next_hub = drone.get_next_hub()
            if not next_hub:
                continue

            current_hub = drone.current_hub

            # --- Rule A: Hub Capacity ---
            dest_hub_obj = self.graph.hubs[next_hub]
            if hub_occupancy[next_hub] >= dest_hub_obj.max_drones:
                logger.debug(
                    f"{drone.id} is waiting: Hub '{next_hub}' is full."
                )
                continue  # Drone stays on its current hub

            # --- Rule B: Connection Bandwidth ---
            # Sort the names alphabetically so (A,B) and (B,A) use the same
            # tracking key
            conn_key = tuple(sorted([current_hub, next_hub]))
            current_usage = link_usage.get(conn_key, 0)
            max_capacity = get_link_capacity(current_hub, next_hub)

            if current_usage >= max_capacity:
                logger.debug(
                    f"{drone.id} is waiting: Connection to '{next_hub}' is "
                    "saturated."
                )
                continue

            # --- Move Approved ! ---
            # Update the physical state so subsequent drones see the new
            # occupancy
            hub_occupancy[current_hub] -= 1
            hub_occupancy[next_hub] += 1
            link_usage[conn_key] = current_usage + 1

            # Update the logical state
            destination = drone.move_forward()
            if destination:
                movements_this_turn.append(f"{drone.id}-{destination}")

        # 3. Logging Phase
        if movements_this_turn:
            log_line = " ".join(movements_this_turn)
            logger.info(log_line)

        # 4. Check Win Condition
        if all(drone.is_delivered for drone in self.drones):
            self.is_finished = True
            logger.debug(f"Simulation completed in {self.current_tick} ticks.")
