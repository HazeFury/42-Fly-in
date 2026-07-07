import heapq
from typing import Dict, List, Optional

from core.graph import Network


def build_adjacency_list(graph_network: Network) -> Dict[str, List[str]]:
    """
    Builds an adjacency list representation of the network graph.

    Args:
        graph_network (Network): The network object containing hubs
        and connections.

    Returns:
        Dict[str, List[str]]: A dictionary mapping each hub name to a list of
        its connected neighbors.
    """
    adj_list: Dict[str, List[str]] = {
        hub_name: [] for hub_name in graph_network.hubs.keys()
    }
    for conn in graph_network.connections:
        adj_list[conn.from_hub.name].append(conn.to_hub.name)
        adj_list[conn.to_hub.name].append(conn.from_hub.name)
    return adj_list


def calculate_dijkstra_path(
    graph_network: Network,
    start_hub: str,
    end_hub: str,
    traffic_penalties: Optional[Dict[str, float]] = None,
) -> Optional[List[str]]:
    """
    Calculates the optimal path between two hubs using a modified Dijkstra's
    algorithm.

    Incorporates custom weights for different zone access types
    (priority, restricted, normal) and applies dynamic micro-penalties to
    prevent traffic congestion on symmetrical routes.

    Args:
        graph_network (Network): The network object representing the map
        topology.
        start_hub (str): The name of the starting hub.
        end_hub (str): The name of the destination hub.
        traffic_penalties (Optional[Dict[str, float]]): Cumulative penalties
        for load balancing across routes.

    Returns:
        Optional[List[str]]: A list of hub names representing the optimal
        path, or None if no path exists.
    """

    adj_list = build_adjacency_list(graph_network)
    priority_queue: List[tuple[float, str]] = [(0.0, start_hub)]

    distances: Dict[str, float] = {
        hub: float("inf") for hub in graph_network.hubs.keys()
    }
    distances[start_hub] = 0.0

    previous_nodes: Dict[str, Optional[str]] = {
        hub: None for hub in graph_network.hubs.keys()
    }

    while priority_queue:
        current_cost, current_hub = heapq.heappop(priority_queue)

        if current_hub == end_hub:
            break

        if current_cost > distances[current_hub]:
            continue

        for neighbor in adj_list[current_hub]:
            neighbor_hub = graph_network.hubs[neighbor]

            if neighbor_hub.access == "blocked":
                continue

            # Determine base weight based on zone access type
            if neighbor_hub.access == "restricted":
                weight = 2.0
            elif neighbor_hub.access == "priority":
                # 0.9 makes it mathematically cheaper than a normal zone (1.0)
                # to win ties, but prevents taking absurdly long detours.
                weight = 0.8
            else:
                weight = 1.0

            # Application de la micro-pénalité
            penalty = (
                traffic_penalties.get(neighbor, 0.0)
                if traffic_penalties
                else 0.0
            )
            new_cost = current_cost + weight + penalty

            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous_nodes[neighbor] = current_hub
                heapq.heappush(priority_queue, (new_cost, neighbor))

    if distances[end_hub] == float("inf"):
        return None

    path: List[str] = []
    current: Optional[str] = end_hub

    while current is not None:
        path.append(current)
        current = previous_nodes[current]

    path.reverse()
    return path
