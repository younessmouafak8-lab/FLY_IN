import heapq
from structure import Connection, Zone
from typing import Dict, List, Optional, Tuple


class Algo:
    """Pathfinding engine for routing drones through a zone graph.

    Wraps a custom Dijkstra search over a pre-built adjacency list,
    accounting for zone movement costs and prior usage so repeated calls
    can surface different candidate paths.

    Attributes:
        data: Adjacency list mapping each zone to its list of neighbors.
        start: The zone drones depart from.
        end: The target zone drones must reach.
        zones: Mapping of zone name to Zone object.
        connections: Mapping of a sorted (zone1, zone2) name pair to its
            Connection object.
    """

    def __init__(self, data: Dict[Zone, List[Zone]], start: Zone, end: Zone,
                 zones: Dict[str, Zone],
                 connections: Dict[Tuple[str, str], Connection]) -> None:
        """Initializes the Algo instance with the graph and its endpoints.

        Args:
            data: Adjacency list mapping each zone to its neighbors.
            start: The zone drones depart from.
            end: The target zone drones must reach.
            zones: Mapping of zone name to Zone object.
            connections: Mapping of a sorted (zone1, zone2) name pair to
                its Connection object.
        """
        self.data = data
        self.start = start
        self.end = end
        self.zones = zones
        self.connections = connections

    def custom_dijkstra(self) -> Optional[List[Zone]]:
        """Finds the cheapest path from start to end via a priority-queue
        search.

        Uses a min-heap keyed on accumulated cost (with a priority-zone
        tie-breaker) to expand the cheapest known zone first. Each visited
        zone's `usage` is nudged upward so that a later call is more
        likely to favor a different route.

        Returns:
            The list of Zone objects from start to end, in order, if a
            path exists; otherwise None.
        """
        i = 1
        queue: List[Tuple[float, int, int, Zone]] = []
        start = self.start
        heapq.heappush(queue, (0, start.is_priority(), i, start))
        cheapest: Dict[Zone, float] = {start: 0}
        parent: Dict[Zone, Optional[Zone]] = {start: None}
        path: List[Zone] = []

        while queue:
            current_cost, is_priority, index, current = heapq.heappop(queue)
            if current == self.end:
                node: Optional[Zone] = current
                while node:
                    path.append(node)
                    node.usage += 0.1
                    node = parent[node]
                return path[::-1]

            for neighbor in self.data[current]:
                if neighbor.type == "blocked":
                    continue
                neighbor_cost = (current_cost + neighbor.get_cost() +
                                 neighbor.usage)
                if neighbor not in cheapest:
                    cheapest[neighbor] = neighbor_cost
                    heapq.heappush(queue, (neighbor_cost,
                                   neighbor.is_priority(), i, neighbor))
                    parent[neighbor] = current
                else:
                    saved_cost = cheapest[neighbor]
                    if saved_cost > neighbor_cost:
                        cheapest[neighbor] = neighbor_cost
                        heapq.heappush(queue, (neighbor_cost,
                                       neighbor.is_priority(), i, neighbor))
                        parent[neighbor] = current
                i += 1
        return None

    def get_path(self) -> Optional[List[Zone]]:
        """Runs a single search for a path from start to end.

        Returns:
            The list of Zone objects from start to end, in order, if a
            path exists; otherwise None.
        """
        return self.custom_dijkstra()

    def get_max(self, connections: Dict[Tuple, Connection], p: Tuple) -> int:
        """Computes the usable capacity of the hop between two zones.

        Compares the connecting link's max capacity against the
        destination zone's max drone capacity and returns the smaller of
        the two, since that's the true bottleneck for that hop.

        Args:
            connections: Mapping of a sorted (zone1, zone2) name pair to
                its Connection object.
            p: A pair whose first two elements are the origin and
                destination Zone objects for this hop.

        Returns:
            The smaller of the connection's max_link_capacity and the
            destination zone's max_drones.
        """
        key = tuple(sorted((p[0].name, p[1].name)))
        cnx = connections[key].max_link_capacity
        return cnx if cnx < p[1].max_drones else p[1].max_drones

    def get_paths(self) -> Optional[List[Tuple[int, int, List[Zone]]]]:
        """Collects distinct candidate paths from start to end.

        Repeatedly calls get_path(), relying on the usage nudge applied
        during each search to surface different routes, until a path
        repeats or no further path is found.

        Returns:
            A list of (capacity, capacity, path) tuples, one per distinct
            path found, where each capacity value is the bottleneck
            capacity of that path's first hop; or None if no path exists
            at all.
        """
        paths: List[List[Zone]] = []
        path = self.get_path()
        if not path:
            return None
        while path not in paths:
            paths.append(path)
            next_path = self.get_path()
            if next_path is None:
                break
            path = next_path
        result = [(self.get_max(self.connections, (p[0], p[1])),
                  self.get_max(self.connections, (p[0], p[1])), p)
                  for p in paths]
        return result
