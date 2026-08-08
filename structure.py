from typing import Dict, List, Tuple


class Zone:
    def __init__(self, name: str, coordinates: Tuple[int, int], type: str,
                 max_drones: int, color: str) -> None:
        self.name = name
        self.coordinates = coordinates
        self.type = type
        self.max_drones = max_drones
        self.color = color
        self.usage: float = 0
        self.drones: int = 0

    def get_cost(self) -> int:
        cost = 0
        if self.type == "normal" or self.type == "priority":
            cost = 1

        if self.type == "restricted":
            cost = 2

        return cost

    def is_priority(self) -> int:
        if self.type == "priority":
            return 0
        return 1


class Connection:
    def __init__(self, zone1: Zone, zone2: Zone,
                 max_link_capacity: int) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.cost: int = 0
        self.max_link_capacity = max_link_capacity
        self.drones: int = 0


class Graph:
    def __init__(self, num_drones: int, start_zone: Zone, end_zone: Zone,
                 zones: Dict[str, Zone],
                 connections: Dict[Tuple, Connection]) -> None:
        self.num_drones = num_drones
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.zones = zones
        self.connections = connections
        self.graph: Dict[Zone, List[Zone]] = {}

    def build_list(self) -> None:
        for zone in self.zones.values():
            tmp: List[Zone] = []
            for con in self.connections.values():
                if zone.name == con.zone1.name:
                    tmp.append(self.zones[con.zone2.name])
                if zone.name == con.zone2.name:
                    tmp.append(self.zones[con.zone1.name])

            self.graph.update({zone: tmp})


class Drone:
    def __init__(self, id: int,
                 path: List[Zone]) -> None:
        self.id = id
        self.path = path
        self.i: int = 0
        self.done: bool = False
        self.in_connection: bool = False
        self.to_move: int = 0
