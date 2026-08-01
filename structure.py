from bfs import bfs


class Graph:
    def __init__(self, num_drones, start_zone, end_zone, zones: dict,
                 connections):
        self.num_drones = num_drones
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.zones = zones
        self.connections = connections
        self.graph = {}

    def build_list(self):
        lst = {}
        for zone in self.zones.values():
            tmp = []
            for con in self.connections:
                if zone.name == con.zone1.name:
                    tmp.append(self.zones[con.zone2.name])
                if zone.name == con.zone2.name:
                    tmp.append(self.zones[con.zone1.name])

            lst.update({zone: tmp})

        print(bfs(lst, self.start_zone, self.end_zone))


class Zone:
    def __init__(self, name: str, coordinates: tuple, type: str,
                 max_drones: int, color: str):
        self.name = name
        self.coordinates = coordinates
        self.type = type
        self.max_drones = max_drones
        self.color = color

    def get_cost(self):
        cost = 0
        if self.type == "normal" or self.type == "priority":
            cost = 1

        if self.type == "restricted":
            cost = 2

        return cost

    def is_priority(self):
        if self.type == "priority":
            return 1
        return 0


class Connection:
    def __init__(self, zone1, zone2, max_link_capacity):
        self.zone1 = zone1
        self.zone2 = zone2
        self.cost = 0
        self.max_link_capacity = max_link_capacity
