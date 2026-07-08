from __future__ import annotations  # Forward declaration for mypy

from typing import Dict, List, Tuple

from utils.models import LevelData


class Hub:
    """
    Represents a node in the drone network.
    Stores its properties and a list of references to its connections.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str,
        max_drones: int = 1,
        access: str = "normal",
        color: str | None = None,
    ) -> None:
        """Initialize the hub with data from the parsed model."""
        self.name: str = name
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones
        self.x: int = x
        self.y: int = y
        self.color = color
        self.access = access
        self.connections: List[Connection] = []

    def add_connection(self, connection: Connection) -> None:
        """Adds a reference to a Connection object."""
        if isinstance(connection, Connection):
            self.connections.append(connection)


class Connection:
    """
    Represents a bidirectional edge between two Hubs.
    """

    def __init__(self, from_hub: Hub, to_hub: Hub, capacity: int) -> None:
        """
        Initialize the connection with direct references to the Hub objects.
        """
        self.from_hub: Hub = from_hub
        self.to_hub: Hub = to_hub
        self.capacity = capacity


class Network:
    """
    The orchestrator that builds and holds the entire graph structure.
    """

    def __init__(self, level_data: LevelData) -> None:
        """
        Initializes the graph by reading the validated Pydantic data.
        """
        self.hubs: Dict[str, Hub] = {}
        self.connections: List[Connection] = []

        self._build_graph(level_data)

    def _build_graph(self, level_data: LevelData) -> None:
        """
        Parses the LevelData to instantiate Hubs and Connections,
        and links them together.
        """
        for zone in level_data.zones:
            new_hub = Hub(
                name=zone.name,
                zone_type=zone.type,
                x=zone.x,
                y=zone.y,
                max_drones=zone.metadata.max_drones
                if zone.type not in ("start_hub", "end_hub")
                else level_data.nb_drones,
                access=zone.metadata.zone,
                color=zone.metadata.color,
            )
            self.hubs[zone.name] = new_hub

        for connection in level_data.connections:
            new_connection = Connection(
                from_hub=self.hubs[connection.from_hub],
                to_hub=self.hubs[connection.to_hub],
                capacity=connection.metadata.max_link_capacity,
            )
            self.connections.append(new_connection)
            self.hubs[connection.from_hub].add_connection(new_connection)
            self.hubs[connection.to_hub].add_connection(new_connection)

    def get_start_and_exit_hub(self) -> Tuple[str, str]:
        """
        Iterates through the network hubs to find and return the exact names
        of the start and end zones.
        """
        start_hub = ""
        end_hub = ""

        for key, hub in self.hubs.items():
            if hub.zone_type == "start_hub":
                start_hub = key
            elif hub.zone_type == "end_hub":
                end_hub = key

        return (start_hub, end_hub)
