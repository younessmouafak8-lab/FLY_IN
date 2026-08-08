import heapq
from structure import Connection, Zone
from typing import Dict, List, Optional, Tuple


class Algo:

    def __init__(self, data: Dict[Zone, List[Zone]], start: Zone, end: Zone,
                 zones: Dict[str, Zone],
                 connections: Dict[Tuple[str, str], Connection]) -> None:
        self.data = data
        self.start = start
        self.end = end
        self.zones = zones
        self.connections = connections

    def custom_dijkstra(self) -> Optional[List[Zone]]:
        i = 1
        queue: List[Tuple[float, int, int, Zone]] = []
        start = self.start
        heapq.heappush(queue, (0, start.is_priority(), i, start))
        cheapest: Dict[Zone, float] = {start: 0}
        parent: Dict[Zone, Optional[Zone]] = {start: None}
        path: List[Zone] = []

        while queue:
            current_cost, ispriority, n, current = heapq.heappop(queue)
            if current_cost > cheapest[current]:
                continue
            if current == self.end:
                node: Optional[Zone] = current
                while node:
                    path.append(node)
                    node.usage += 0.01
                    node = parent[node]
                return path[::-1]

            for neighbor in self.data[current]:
                if neighbor.type == "blocked":
                    continue
                cost = current_cost + neighbor.get_cost() + neighbor.usage
                if neighbor not in cheapest:
                    cheapest[neighbor] = cost
                    heapq.heappush(queue, (cost, neighbor.is_priority(), i,
                                           neighbor))
                    parent[neighbor] = current
                else:
                    saved_cost = cheapest[neighbor]
                    if cost < saved_cost:
                        cheapest[neighbor] = cost
                        heapq.heappush(queue, (cost, neighbor.is_priority(),
                                               i, neighbor))
                        parent[neighbor] = current
                i += 1
        return None

    def get_path(self) -> Optional[List[Zone]]:
        return self.custom_dijkstra()

    def get_max(self, connections: Dict[Tuple, Connection], p: Tuple):
        key = tuple(sorted((p[0].name, p[1].name)))
        cnx = connections[key].max_link_capacity
        return cnx if cnx < p[1].max_drones else p[1].max_drones

    def get_paths(self) -> Optional[List[Tuple[int, int, List[Zone]]]]:
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
