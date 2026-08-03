class Simulation:
    def __init__(self, connections, zones):
        self.drones = []
        self.connections = connections
        self.zones = zones
        self.zones_usage = {}
        self.link_usage = {}
        self.all_done = False
        self.turn = 0

    def check_drones(self):
        return all([drone.done for drone in self.drones])

    def is_movable(self, zone_from, zone_to, drone):
        flag = True
        key = tuple(sorted((zone_from.name, zone_to.name)))
        connection = self.connections[key]
        conection_usage = self.link_usage.get((key, self.turn + 1), 0)

        if zone_to.type == "restricted":
            conection_usage2 = self.link_usage.get((key, self.turn + 2), 0)
            zone_usage = self.zones_usage.get((zone_to.name, self.turn + 2), 0)
            if conection_usage >= connection.max_link_capacity or\
                    conection_usage2 >= connection.max_link_capacity:
                flag = False

            if zone_usage >= zone_to.max_drones:
                flag = False

            if not flag:
                from_zone_usage = self.zones_usage.get((zone_from.name,
                                                   self.turn + 1), 0)
                self.zones_usage[(zone_from.name, self.turn + 1)] = from_zone_usage + 1
            else:
                self.zones_usage[(zone_to.name, self.turn + 2)] = zone_usage + 1
                self.link_usage[(key, self.turn + 1)] = conection_usage + 1
                self.link_usage[(key, self.turn + 2)] = conection_usage2 + 1

        else:
            zone_usage = self.zones_usage.get((zone_to.name, self.turn + 1), 0)
            if conection_usage >= connection.max_link_capacity:
                flag = False

            if zone_usage >= zone_to.max_drones:
                flag = False

            if not flag:
                from_zone_usage = self.zones_usage.get((zone_from.name,
                                                   self.turn + 1), 0)
                self.zones_usage[(zone_from.name, self.turn + 1)] = from_zone_usage + 1
            else:
                self.zones_usage[(zone_to.name, self.turn + 1)] = zone_usage + 1
                self.link_usage[(key, self.turn + 1)] = conection_usage + 1

        return flag

    def simulate(self):
        while not self.all_done:

            for drone in self.drones:
                if drone.i >= len(drone.path) - 1:
                    drone.done = True
                    continue
                from_zone, cost = drone.path[drone.i]
                to_zone, cost = drone.path[drone.i + 1]

                if drone.in_connection:
                    drone.to_move -= 1
                    if not drone.to_move:
                        drone.in_connection = False
                        drone.i += 1
                        print(f"drone{drone.id} reached {to_zone.name} on turn {self.turn + 1}")
                    continue

                if self.is_movable(from_zone, to_zone, drone):
                    if to_zone.type == "restricted":
                        drone.in_connection = True
                        drone.to_move = 2
                        print(f"drone{drone.id} departed towards {to_zone.name} on turn {self.turn + 1}")
                    else:
                        drone.i += 1
                        print(f"drone{drone.id} moved to {to_zone.name} on turn {self.turn + 1}")

            if self.check_drones():
                self.all_done = True

            self.turn += 1
        print(self.zones_usage)
