from typing import Dict, List, Tuple


class Zone:
    """A single node in the drone routing network.

    Represents one hub from the map file, along with the movement rules
    and current usage state that affect pathfinding and simulation.

    Attributes:
        name: The zone's unique name.
        coordinates: The zone's (x, y) position.
        type: One of "normal", "blocked", "restricted", or "priority".
        max_drones: The maximum number of drones allowed in this zone at
            once (ignored for start/end zones by the parser).
        color: The zone's display color, as a hex string or "rainbow".
        usage: A running tally nudged up each time a path through this
            zone is found, used to steer later searches toward less-used
            zones.
        drones: Reserved for tracking live drone occupancy, if used.
    """

    def __init__(self, name: str, coordinates: Tuple[int, int], type: str,
                 max_drones: int, color: str) -> None:
        """Initializes a Zone with its static map data.

        Args:
            name: The zone's unique name.
            coordinates: The zone's (x, y) position.
            type: One of "normal", "blocked", "restricted", or
                "priority".
            max_drones: The maximum number of drones allowed in this
                zone at once.
            color: The zone's display color, as a hex string or
                "rainbow".
        """
        self.name = name
        self.coordinates = coordinates
        self.type = type
        self.max_drones = max_drones
        self.color = color
        self.usage: float = 0

    def get_cost(self) -> int:
        """Returns the turn cost to move into this zone.

        Returns:
            2 for a restricted zone, 1 for normal or priority, and 0
            for any other type (e.g. blocked, which should never
            actually be entered).
        """
        cost = 0
        if self.type == "normal" or self.type == "priority":
            cost = 1

        if self.type == "restricted":
            cost = 2

        return cost

    def is_priority(self) -> int:
        """Returns this zone's tie-breaking rank for the search heap.

        Returns:
            0 if this zone is a priority zone (sorts first on a cost
            tie), 1 otherwise.
        """
        if self.type == "priority":
            return 0
        return 1


class Connection:
    """A bidirectional link between two zones.

    Attributes:
        zone1: One endpoint of the connection.
        zone2: The other endpoint of the connection.
        cost: Reserved for a per-connection cost, currently unused
            (actual movement cost comes from the destination Zone).
        max_link_capacity: The maximum number of drones allowed to
            traverse this connection simultaneously.
        drones: Reserved for tracking live drone occupancy, if used.
    """

    def __init__(self, zone1: Zone, zone2: Zone,
                 max_link_capacity: int) -> None:
        """Initializes a Connection between two zones.

        Args:
            zone1: One endpoint of the connection.
            zone2: The other endpoint of the connection.
            max_link_capacity: The maximum number of drones allowed to
                traverse this connection simultaneously.
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.cost: int = 0
        self.max_link_capacity = max_link_capacity


class Graph:
    """Builds and holds the adjacency list for the zone network.

    Attributes:
        num_drones: The total number of drones to route through the
            network.
        start_zone: The zone drones depart from.
        end_zone: The target zone drones must reach.
        zones: Mapping of zone name to Zone object.
        connections: Mapping of a sorted (zone1, zone2) name pair to its
            Connection object.
        graph: The adjacency list, mapping each Zone to the list of Zone
            objects it's directly connected to. Empty until build_list()
            is called.
    """

    def __init__(self, num_drones: int, start_zone: Zone, end_zone: Zone,
                 zones: Dict[str, Zone],
                 connections: Dict[Tuple, Connection]) -> None:
        """Initializes the Graph with its zones and connections.

        Args:
            num_drones: The total number of drones to route through the
                network.
            start_zone: The zone drones depart from.
            end_zone: The target zone drones must reach.
            zones: Mapping of zone name to Zone object.
            connections: Mapping of a sorted (zone1, zone2) name pair to
                its Connection object.
        """
        self.num_drones = num_drones
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.zones = zones
        self.connections = connections
        self.graph: Dict[Zone, List[Zone]] = {}

    def build_list(self) -> None:
        """Builds self.graph, the adjacency list, from self.connections.

        For every zone, scans all connections to find the zones it's
        directly linked to (in either direction, since connections are
        bidirectional) and records them as that zone's neighbors.
        """
        for zone in self.zones.values():
            tmp: List[Zone] = []
            for con in self.connections.values():
                if zone.name == con.zone1.name:
                    tmp.append(self.zones[con.zone2.name])
                if zone.name == con.zone2.name:
                    tmp.append(self.zones[con.zone1.name])

            self.graph.update({zone: tmp})


class Drone:
    """Tracks one drone's assigned path and progress through it.

    Attributes:
        id: The drone's unique identifier.
        path: The ordered list of Zone objects from start to end that
            this drone will follow.
        i: The index into path of the drone's current position.
        done: Whether this drone has reached the end of its path.
        in_connection: Whether the drone is currently mid-transit
            through a multi-turn (restricted) connection.
    """

    def __init__(self, id: int,
                 path: List[Zone]) -> None:
        """Initializes a Drone with its assigned path.

        Args:
            id: The drone's unique identifier.
            path: The ordered list of Zone objects from start to end
                that this drone will follow.
        """
        self.id = id
        self.path = path
        self.i: int = 0
        self.done: bool = False
        self.in_connection: bool = False
