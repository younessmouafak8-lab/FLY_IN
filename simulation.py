from typing import Dict, List, Tuple

from structure import Connection, Drone, Zone
from rich import print as my_print


class Simulation:
    """Replays precomputed drone paths turn by turn under capacity limits.

    Assigns each drone one of the precomputed candidate paths, then
    steps through turns, moving drones one hop at a time while enforcing
    zone occupancy (max_drones) and connection capacity
    (max_link_capacity), including the two-turn transit rule for
    restricted zones. Movement is printed to the terminal as it happens.

    Attributes:
        nb_drones: The total number of drones to simulate.
        connections: Mapping of a sorted (zone1, zone2) name pair to its
            Connection object.
        zones: Mapping of zone name to Zone object.
        paths: A list of (remaining_capacity, max_capacity, path) tuples,
            one per candidate path, used to round-robin drones across
            distinct routes.
        drones: The Drone objects created so far, one per drone.
        zones_usage: Mapping of (zone_name, turn) to the number of
            drones occupying that zone on that turn.
        link_usage: Mapping of (connection_key, turn) to the number of
            drones using that connection on that turn.
        all_done: Whether every drone has reached its destination.
        turn: The current simulation turn, starting at 0.
    """

    def __init__(self, nb_drones: int,
                 connections: Dict[Tuple, Connection],
                 zones: Dict[str, Zone],
                 paths: List[Tuple[int, int, List[Zone]]]) -> None:
        """Initializes the simulation with its drones' candidate paths.

        Args:
            nb_drones: The total number of drones to simulate.
            connections: Mapping of a sorted (zone1, zone2) name pair to
                its Connection object.
            zones: Mapping of zone name to Zone object.
            paths: A list of (remaining_capacity, max_capacity, path)
                tuples, one per candidate path found by the pathfinder.
        """
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
        """Assigns each drone one of the candidate paths, round-robin.

        Walks through self.paths in order, giving each drone the next
        path that still has remaining capacity and decrementing that
        path's remaining count. Once every path's remaining capacity
        hits zero, all paths are refilled to their max capacity so
        distribution can continue. Populates self.drones with one Drone
        per iteration, up to self.nb_drones.
        """
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
        """Checks whether every drone has finished its path.

        Returns:
            True if all drones are marked done, False otherwise.
        """
        return all([drone.done for drone in self.drones])

    def is_movable(self, zone_from: Zone, zone_to: Zone) -> bool:
        """Checks capacity for a hop and reserves it if the move is allowed.

        For a restricted destination zone, checks the connection's
        capacity for the upcoming turn and the destination zone's
        capacity across both turns of its two-turn transit. For any
        other destination, checks the connection and destination zone's
        capacity for the single upcoming turn. If the move is allowed,
        reserves the corresponding zone/link usage slots immediately;
        otherwise records the drone as staying in its current zone for
        the next turn.

        Args:
            zone_from: The zone the drone is currently in.
            zone_to: The zone the drone is attempting to move into.

        Returns:
            True if the move is allowed (and has been reserved), False
            if capacity is unavailable and the drone must wait.
        """
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
        """Wraps a zone's name in rich markup matching its color.

        If the zone's color is "rainbow", each character of the name is
        wrapped in a different color from a fixed rotating palette.
        Otherwise, the whole name is wrapped in the zone's own color.

        Args:
            zone: The Zone whose name should be colored.

        Returns:
            The zone's name as a rich-markup string ready to print.
        """
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
        """Runs the turn-by-turn simulation until every drone arrives.

        Each turn, every drone either continues an in-progress restricted
        transit, waits because its next hop isn't currently movable, or
        advances one hop, printing its movement as it happens. A drone
        moving into a restricted zone is marked in-transit for one
        additional turn before it's considered arrived. The simulation
        ends once every drone has reached its destination.
        """
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
