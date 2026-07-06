from typing import Any, List

from core.pathfinding import calculate_dijkstra_path
from utils.logger import logger


class LogicalDrone:
    """
    Represents the logical state of a drone in the network.
    """

    def __init__(
        self, drone_id: str, start_hub: str, optimal_path: List[str]
    ) -> None:
        self.id = drone_id
        # current_hub becomes None when the drone is flying between hubs
        self.current_hub: str | None = start_hub
        self.path = optimal_path
        self.path_index = 0
        self.is_delivered = False

        # --- Transit State Properties ---
        self.transit_destination: str | None = None
        self.transit_conn_name: str | None = None

    def get_next_hub(self) -> str | None:
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None

    def start_transit(self, next_hub: str, connection_name: str) -> None:
        """Initiates a 2-turn flight toward a restricted zone."""
        self.transit_destination = next_hub
        self.transit_conn_name = connection_name
        self.current_hub = None  # The drone leaves the ground

    def finish_transit(self) -> str:
        """Completes the flight and lands on the restricted zone."""
        assert self.transit_destination is not None
        arrived_at = self.transit_destination

        self.current_hub = arrived_at
        self.path_index += 1
        if self.path_index == len(self.path) - 1:
            self.is_delivered = True

        # Clear transit state
        self.transit_destination = None
        self.transit_conn_name = None

        return arrived_at

    def move_forward(self) -> str | None:
        """Instant travel (1-turn) for normal/priority zones."""
        next_hub = self.get_next_hub()
        if next_hub:
            self.current_hub = next_hub
            self.path_index += 1
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
        Creates all drones, dynamically distributing traffic across perfectly
        symmetrical routes using a micro-penalty tie-breaker.
        """
        start_hub, end_hub = self.graph.get_start_and_exit_hub()

        traffic_penalties: dict[str, float] = {}

        for i in range(nb_drones):
            optimal_path = calculate_dijkstra_path(
                self.graph, start_hub, end_hub, traffic_penalties
            )

            if not optimal_path:
                logger.critical(
                    "Cannot initialize simulation for "
                    f"Drone D{i + 1}: No path found!"
                )
                return

            logger.debug(f"Drone D{i + 1} path: {' -> '.join(optimal_path)}")

            # On ajoute un micro-poids. Il cassera l'ordre alphabétique
            # pour répartir sur les chemins de même distance, sans jamais
            # provoquer de détours absurdes.
            for hub in optimal_path:
                if hub not in (start_hub, end_hub):
                    traffic_penalties[hub] = (
                        traffic_penalties.get(hub, 0.0) + 0.00001
                    )

            self.drones.append(
                LogicalDrone(f"D{i + 1}", start_hub, optimal_path)
            )

    def next_tick(self) -> None:
        if self.is_finished:
            return

        self.current_tick += 1
        movements_this_turn: List[str] = []

        # 1. Snapshot occupancy (Include drones in transit to secure their
        # landing spot!)
        hub_occupancy = {hub_name: 0 for hub_name in self.graph.hubs.keys()}
        for drone in self.drones:
            if not drone.is_delivered:
                if drone.transit_destination:
                    hub_occupancy[drone.transit_destination] += 1
                elif drone.current_hub:
                    hub_occupancy[drone.current_hub] += 1

        link_usage: dict[tuple[str, str], int] = {}

        def get_link_capacity(hub_a: str, hub_b: str) -> int:
            for conn in self.graph.connections:
                if (
                    conn.from_hub.name == hub_a and conn.to_hub.name == hub_b
                ) or (
                    conn.from_hub.name == hub_b and conn.to_hub.name == hub_a
                ):
                    return int(conn.capacity)
            return 1

        # 2. Process Drones Sequentially
        for drone in self.drones:
            if drone.is_delivered:
                continue

            # --- RULE A: Is the drone already flying? ---
            if drone.transit_destination:
                arrived_hub = drone.finish_transit()
                movements_this_turn.append(f"{drone.id}-{arrived_hub}")
                continue

            # --- RULE B: The drone is on a hub and wants to move ---
            next_hub = drone.get_next_hub()
            if not next_hub:
                continue

            current_hub = drone.current_hub

            if current_hub is None:
                continue

            dest_hub_obj = self.graph.hubs[next_hub]

            # Check Hub Capacity
            if hub_occupancy[next_hub] >= dest_hub_obj.max_drones:
                continue

            # Check Connection Bandwidth
            conn_key: tuple[str, str] = (
                min(current_hub, next_hub),
                max(current_hub, next_hub),
            )
            current_usage = link_usage.get(conn_key, 0)
            max_capacity = get_link_capacity(current_hub, next_hub)

            if current_usage >= max_capacity:
                continue

            # Move Approved: Update physical limits for subsequent drones
            hub_occupancy[current_hub] -= 1
            hub_occupancy[next_hub] += 1
            link_usage[conn_key] = current_usage + 1

            # Is it a restricted zone requiring a flight?
            if dest_hub_obj.access == "restricted":
                # Fallback connection name. Modify this if your parser
                # extracts real connection names.
                conn_name = f"conn_{current_hub}-{next_hub}"
                drone.start_transit(next_hub, conn_name)
                movements_this_turn.append(f"{drone.id}-{conn_name}")
            else:
                # Instant jump (normal/priority zones)
                destination = drone.move_forward()
                movements_this_turn.append(f"{drone.id}-{destination}")

        # 3. Logging & Win Condition
        if movements_this_turn:
            logger.info(" ".join(movements_this_turn))

        if all(drone.is_delivered for drone in self.drones):
            self.is_finished = True
            logger.debug(f"Simulation completed in {self.current_tick} ticks.")
