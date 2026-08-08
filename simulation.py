from typing import Dict, List, Tuple

from structure import Connection, Drone, Zone
from rich import print as my_print


class Simulation:
    def __init__(self, nb_drones: int,
                 connections: Dict[Tuple, Connection],
                 zones: Dict[str, Zone],
                 paths: List[Tuple[int, int, List[Zone]]]) -> None:
        self.nb_drones = nb_drones
        self.connections = connections
        self.zones = zones
        self.paths = paths
        self.drones: List[Drone] = []
        self.zones_usage: Dict[Tuple[str, int], int] = {}
        self.link_usage: Dict[Tuple[Tuple, int], int] = {}
        self.all_done = False
        self.turn = 0

    def distribute_paths(self) -> None:
        i = 0
        while i < self.nb_drones:

            if all([not p[0] for p in self.paths]):
                for j, p in enumerate(self.paths):
                    self.paths[j] = (self.paths[j][1], self.paths[j][1],
                                     self.paths[j][2])

            for j, p in enumerate(self.paths):
                if not p[0]:
                    continue

                self.paths[j] = (self.paths[j][0] - 1, self.paths[j][1],
                                 self.paths[j][2])

                drone = Drone(i + 1, p[2])
                self.drones.append(drone)
                break
            i += 1

    def check_drones(self) -> bool:
        return all([drone.done for drone in self.drones])

    def is_movable(self, zone_from: Zone, zone_to: Zone) -> bool:
        flag = True
        key = tuple(sorted((zone_from.name, zone_to.name)))
        connection = self.connections[key]
        conection_usage = self.link_usage.get((key, self.turn + 1), 0)

        if zone_to.type == "restricted":
            zone_usage = self.zones_usage.get((zone_to.name, self.turn + 1),
                                              0)
            zone_usage2 = self.zones_usage.get((zone_to.name, self.turn + 2),
                                               0)
            if conection_usage >= connection.max_link_capacity:
                flag = False

            if zone_usage >= zone_to.max_drones or \
                    zone_usage2 >= zone_to.max_drones:
                flag = False

            if not flag:
                from_zone_usage = self.zones_usage.get((zone_from.name,
                                                        self.turn + 1), 0)
                self.zones_usage[(zone_from.name,
                                  self.turn + 1)] = from_zone_usage + 1
            else:
                self.zones_usage[(zone_to.name,
                                  self.turn + 1)] = zone_usage + 1
                self.zones_usage[(zone_to.name,
                                  self.turn + 2)] = zone_usage2 + 1
                self.link_usage[(key, self.turn + 1)] = conection_usage + 1

        else:
            zone_usage = self.zones_usage.get((zone_to.name, self.turn + 1),
                                              0)
            if conection_usage >= connection.max_link_capacity:
                flag = False

            if zone_usage >= zone_to.max_drones:
                flag = False

            if not flag:
                from_zone_usage = self.zones_usage.get((zone_from.name,
                                                        self.turn + 1), 0)
                self.zones_usage[(zone_from.name,
                                  self.turn + 1)] = from_zone_usage + 1
            else:
                self.zones_usage[(zone_to.name,
                                  self.turn + 1)] = zone_usage + 1
                self.link_usage[(key, self.turn + 1)] = conection_usage + 1

        return flag

    def get_name_color(self, zone: Zone) -> str:
        if zone.color == "rainbow":
            colors = ["red", "orange1", "yellow", "green", "cyan", "blue",
                      "magenta"]
            colored_name = ""
            for i, char in enumerate(zone.name):
                color = colors[i % len(colors)]
                colored_name += f"[{color}]{char}[/{color}]"
        else:
            colored_name = f"[{zone.color}]{zone.name}[/{zone.color}]"
        return colored_name

    def simulate(self) -> None:
        while not self.all_done:

            for drone in self.drones:
                if drone.i >= len(drone.path) - 1:
                    drone.done = True
                    continue
                from_zone = drone.path[drone.i]
                to_zone = drone.path[drone.i + 1]

                if drone.in_connection:
                    drone.to_move -= 1
                    if not drone.to_move:
                        drone.in_connection = False
                        drone.i += 1
                        to_zone_name = self.get_name_color(to_zone)
                        my_print(f"D{drone.id}-{to_zone_name}", end=" ")
                    continue

                if self.is_movable(from_zone, to_zone):
                    to_zone_name = self.get_name_color(to_zone)
                    from_zone_name = self.get_name_color(from_zone)
                    if to_zone.type == "restricted":
                        drone.in_connection = True
                        drone.to_move = 1
                        my_print(f"D{drone.id}-{from_zone_name}-"
                                 f"{to_zone_name}", end=" ")
                    else:
                        drone.i += 1
                        my_print(f"D{drone.id}-{to_zone_name} ", end="")
            print()

            if self.check_drones():
                self.all_done = True

            self.turn += 1
