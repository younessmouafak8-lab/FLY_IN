class Graph:
    def __init__(self, num_drones, start_zone, end_zone, zones: dict, connections):
        self.num_drones = num_drones
        self.zones = zones
        self.connections = connections

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

        print(lst)


class Zone:
    def __init__(self, name: str, coordinates: tuple, type: str,
                 max_drones: int, color: str):
        self.name = name
        self.coordinates = coordinates
        self.type = type
        self.max_drones = max_drones
        self.color = color


class Connection:
    def __init__(self, zone1, zone2, max_link_capacity):
        self.zone1 = zone1
        self.zone2 = zone2
        self.cost = 0
        self.max_link_capacity = max_link_capacity
