import heapq
from typing import Any, Dict, List, Optional


def build_adjacency_list(graph_network: Any) -> Dict[str, List[str]]:
    """
    Transforms the raw connections into a fast adjacency list dictionary.
    Example: {'hub_A': ['hub_B', 'hub_C'], 'hub_B': ['hub_A']}
    """
    adj_list: Dict[str, List[str]] = {
        hub_name: [] for hub_name in graph_network.hubs.keys()
    }

    for conn in graph_network.connections:
        adj_list[conn.from_hub].append(conn.to_hub)
        adj_list[conn.to_hub].append(conn.from_hub)

    return adj_list


def calculate_dijkstra_path(
    graph_network: Any, start_hub: str, end_hub: str
) -> Optional[List[str]]:
    """
    Calculates the most optimal path using Dijkstra's algorithm, taking
    into account the specific movement costs of different zone types.

    Returns:
        A list of hub names representing the path
        (e.g., ['start', 'hub_A', 'end']),
        or None if no valid path is found.
    """
    adj_list = build_adjacency_list(graph_network)

    # Priority queue stores tuples of: (accumulated_cost, current_hub_name)
    priority_queue: List[tuple[int, str]] = [(0, start_hub)]

    # Track the absolute minimum cost required to reach each node
    distances: Dict[str, float] = {
        hub: float("inf") for hub in graph_network.hubs.keys()
    }
    distances[start_hub] = 0

    # Track "how we got here" to reconstruct the path backwards at the end
    previous_nodes: Dict[str, Optional[str]] = {
        hub: None for hub in graph_network.hubs.keys()
    }

    while priority_queue:
        # Pop the hub with the lowest accumulated cost so far
        current_cost, current_hub = heapq.heappop(priority_queue)

        # If we reached our destination, we can stop exploring this branch
        if current_hub == end_hub:
            break

        # Optimization: If we found a shorter path to this hub in the meantime,
        # ignore this outdated queue entry
        if current_cost > distances[current_hub]:
            continue

        # Explore neighbors
        for neighbor in adj_list[current_hub]:
            neighbor_metadata = graph_network.hubs[neighbor].metadata

            # 1. Absolute wall: do not enter blocked zones
            if neighbor_metadata.zone == "blocked":
                continue

            # 2. Determine the movement cost to enter this zone
            # Restricted zones take 2 turns to enter, normal/priority take 1.
            weight = 2 if neighbor_metadata.zone == "restricted" else 1

            new_cost = current_cost + weight

            # If we found a strictly better path to this neighbor
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous_nodes[neighbor] = current_hub
                heapq.heappush(priority_queue, (new_cost, neighbor))

    # --- Path Reconstruction ---
    # If the end_hub's distance is still infinity, it means it was
    # completely walled off
    if distances[end_hub] == float("inf"):
        return None

    path: List[str] = []
    current: Optional[str] = end_hub

    # Trace back from end to start using our history
    while current is not None:
        path.append(current)
        current = previous_nodes[current]

    # The path was built backwards (end -> start), so we reverse it
    path.reverse()

    return path
