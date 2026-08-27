import sys
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from structure import Zone, Connection
import webcolors


class Parse:
    """Parses a map configuration file into Zone and Connection objects.

    Reads the custom map file format (nb_drones/start_hub/hub/end_hub/
    connection lines), validates each field against the spec's rules,
    and stores the resulting graph data as attributes on the instance.

    Attributes:
        nb_drones: The number of drones declared in the file.
        start_zone: The parsed start Zone.
        end_zone: The parsed end Zone.
        zones: Mapping of zone name to Zone object.
        connections: Mapping of a sorted (zone1, zone2) name pair to its
            Connection object.
    """

    def __init__(self) -> None:
        """Initializes an empty Parse instance with no file read yet."""
        self.nb_drones: int = 0
        self.start_zone: Zone
        self.end_zone: Zone
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[Tuple[str, str], Connection] = {}

    def is_skippable(self, line: str) -> bool:
        """Checks whether a line is blank or a comment.

        Args:
            line: The stripped text of a single line from the map file.

        Returns:
            True if the line is empty or comment-only, False otherwise.
        """
        pattern = r"^\s*(#.*)?$"
        result = re.match(pattern, line)
        if not result:
            return False
        return True

    def drones_num(self, line: Tuple[int, str]) -> str:
        """Extracts the drone count from an ``nb_drones`` line.

        Args:
            line: A (line_number, text) pair for the line being parsed.

        Returns:
            The drone count, as a string, exactly as captured by the
            regex.

        Raises:
            ValueError: If the line doesn't match the expected
                ``nb_drones: <number>`` format.
        """
        i, text = line
        pattern = r"nb_drones: ([\-\+]?\d+)\s*(?:\s*#.*)?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid drones number field '{text}'")
        return result.group(1)

    def get_start(self, line: Tuple[int, str]) -> Tuple[Optional[str], ...]:
        """Parses a ``start_hub`` line into its raw field groups.

        Args:
            line: A (line_number, text) pair for the line being parsed.

        Returns:
            The regex match groups: name, x, y, and up to three optional
            ``key=value`` metadata fields.

        Raises:
            ValueError: If the line doesn't match the expected
                ``start_hub`` format.
        """
        i, text = line
        pattern = (r"start_hub: ([^\-\s]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\S]+)(?:\s+(\w+=[\S]+))?"
                   r"(?:\s+(\w+=[\S]+))?\])?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid start hub field {text}")
        return (result.groups())

    def get_hubs(self, line: Tuple[int, str]) -> Tuple[Optional[str], ...]:
        """Parses a regular ``hub`` line into its raw field groups.

        Args:
            line: A (line_number, text) pair for the line being parsed.

        Returns:
            The regex match groups: name, x, y, and up to three optional
            ``key=value`` metadata fields.

        Raises:
            ValueError: If the line doesn't match the expected ``hub``
                format.
        """
        i, text = line
        pattern = (r"hub: ([^\-\s]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\S]+)(?:\s+(\w+=[\S]+))?"
                   r"(?:\s+(\w+=[\S]+))?\])?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid hub field {text}")
        return (result.groups())

    def get_end(self, line: Tuple[int, str]) -> Tuple[Optional[str], ...]:
        """Parses an ``end_hub`` line into its raw field groups.

        Args:
            line: A (line_number, text) pair for the line being parsed.

        Returns:
            The regex match groups: name, x, y, and up to three optional
            ``key=value`` metadata fields.

        Raises:
            ValueError: If the line doesn't match the expected
                ``end_hub`` format.
        """
        i, text = line
        pattern = (r"end_hub: ([^\-\s]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\S]+)(?:\s+(\w+=[\S]+))?"
                   r"(?:\s+(\w+=[\S]+))?\])?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid end hub field")
        return (result.groups())

    def get_connection(self, line: Tuple[int, str]
                       ) -> Tuple[Optional[str], ...]:
        """Parses a ``connection`` line into its raw field groups.

        Args:
            line: A (line_number, text) pair for the line being parsed.

        Returns:
            The regex match groups: the two connected zone names, and an
            optional ``max_link_capacity`` value.

        Raises:
            ValueError: If the line doesn't match the expected
                ``connection`` format.
        """
        i, text = line
        pattern = (r"connection: ([^\-\s]+)-([^\-\s]+)"
                   r"(?:\s+\[max_link_capacity=([\-\+]?\d+)\])?\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid connection field '{text}'")
        return (result.groups())

    def is_there(self, nb: Optional[int], start: Optional[Any],
                 end: Optional[Any],
                 connections: Dict[Tuple[str, str], Connection]) -> None:
        """Confirms the required top-level fields were all present.

        Args:
            nb: The parsed drone count, or None if never set.
            start: The parsed start zone, or None if never set.
            end: The parsed end zone, or None if never set.
            connections: The parsed connections mapping.

        Raises:
            ValueError: If any of the drone count, start zone, end zone,
                or connections are missing.
        """
        if not nb:
            raise ValueError("You must provide the number of drones!\n")
        if not start:
            raise ValueError("You must provide a start hub!, start_hub: <name>"
                             " <x> <y> [metadata]")
        if not end:
            raise ValueError("You must provide a end hub!, end_hub: <name> <x>"
                             " <y> [metadata]")
        if not connections:
            raise ValueError("You must provide connections!, connection:"
                             " <name1>-<name2> [metadata]")

    def verify_metadata(self, hub: Tuple[Optional[str], ...],
                        i: int) -> Dict[str, Any]:
        """Validates and normalizes a hub's optional metadata fields.

        Checks each ``key=value`` metadata entry against the allowed
        names and value rules (zone type, positive max_drones, and
        color, converting valid color names to hex or defaulting to
        white).

        Args:
            hub: The raw regex groups for a hub line, as returned by
                get_start/get_hubs/get_end.
            i: The 1-based line number, used in error messages.

        Returns:
            A dict with the resolved "type", "max_drones", and "color"
            values, defaulting to "normal", 1, and "white" respectively
            for anything not specified.

        Raises:
            ValueError: If a metadata name is unknown, duplicated, or
                has an invalid value for its key.
        """
        allowed_names = ("color", "max_drones", "zone")
        allowed_zones = ("normal", "blocked", "restricted", "priority")
        temp: Set[str] = set()
        data: Dict[str, Any] = {"type": "normal", "max_drones": 1,
                                "color": "white"}
        for name in hub[3:]:
            if name:
                parts = name.split("=")
                key = parts[0]
                value: Any = parts[1]
                if key not in allowed_names:
                    raise ValueError(f"line {i}: invalid name '{key}'")
                if key not in temp:
                    temp.add(key)
                else:
                    raise ValueError(f"line {i}: duplicated name '{key}'")
                if key == "zone":
                    if value not in allowed_zones:
                        raise ValueError(f"line {i}: invalid zone type "
                                         f"{key}:{value}")
                    data.update({"type": value})
                if key == "max_drones":
                    try:
                        value = int(value)
                        if value <= 0:
                            raise ValueError()
                        data.update({key: value})
                    except ValueError:
                        raise ValueError(f"line {i}: value for max_drones must"
                                         f" be a positive integer. '{value}'")
                if key == "color":
                    if value != "rainbow":
                        try:
                            value = webcolors.name_to_hex(value)
                        except ValueError:
                            value = webcolors.name_to_hex("white")
                    data.update({key: value})
        return data

    def validate_hub(self, hub: Tuple, i: int) -> Zone:
        """Builds a Zone object from a hub's parsed fields.

        Args:
            hub: The raw regex groups for a hub line, as returned by
                get_start/get_hubs/get_end.
            i: The line number, used in error messages.

        Returns:
            A new Zone constructed from the hub's name, coordinates, and
            validated metadata.
        """
        values = {"name": hub[0],
                  "coordinates": (int(hub[1]), int(hub[2]))}
        values.update(self.verify_metadata(hub, i))
        return Zone(**values)

    def validate_connection(self, connection: Tuple[Optional[str], ...],
                            hubs: Dict[str, Zone], i: int) -> Connection:
        """Builds a Connection object from a connection line's fields.

        Args:
            connection: The raw regex groups for a connection line, as
                returned by get_connection.
            hubs: Mapping of zone name to Zone object, used to resolve
                the connection's endpoints.
            i: The 1-based line number, used in error messages.

        Returns:
            A new Connection linking the two named zones, with
            max_link_capacity defaulting to 1 if not specified.

        Raises:
            ValueError: If max_link_capacity is present but not a
                positive integer.
        """
        con: Dict[str, Any] = {"zone1": hubs[connection[0]],  # type: ignore
                               "zone2": hubs[connection[1]]}  # type: ignore
        val = {"max_link_capacity": 1}
        if connection[2]:
            num = int(connection[2])
            if num <= 0:
                raise ValueError(f"line {i}: max_link_capacity must be a "
                                 "positive integer.")
            val["max_link_capacity"] = num
        con.update(val)
        return Connection(**con)

    def validate_zones(self, zone: Zone, valid_zones: Set[str],
                       valid_coordinates: Set[Tuple[int, int]],
                       i: int) -> None:
        """Checks a zone for duplicate name or coordinates, then records it.

        Args:
            zone: The Zone to validate.
            valid_zones: The running set of zone names seen so far;
                updated in place.
            valid_coordinates: The running set of coordinates seen so
                far; updated in place.
            i: The line number, used in error messages.

        Raises:
            ValueError: If the zone's name or coordinates were already
                used by an earlier zone.
        """
        if zone.name in valid_zones:
            raise ValueError(f"line {i}: duplicate zone names are "
                             f"not tolerated '{zone.name}'")
        valid_zones.add(zone.name)
        if zone.coordinates in valid_coordinates:
            raise ValueError(f"Line {i}: duplicated "
                             "coordinates")
        valid_coordinates.add(zone.coordinates)

    def validate_start_end(self, start: Zone, end: Zone) -> None:
        """Confirms neither the start nor end zone is blocked.

        Args:
            start: The parsed start Zone.
            end: The parsed end Zone.

        Raises:
            ValueError: If the start or end zone's type is "blocked".
        """
        if start.type == 'blocked':
            raise ValueError("start zone cant be blocked")
        if end.type == 'blocked':
            raise ValueError("end zone cant be blocked")

    def parse_file(self) -> None:
        """Reads and parses the map file given as the first CLI argument.

        Walks the file line by line, dispatching each to the matching
        handler based on its prefix (nb_drones/start_hub/hub/end_hub/
        connection), validating as it goes, and populating self.zones,
        self.connections, self.start_zone, self.end_zone, and
        self.nb_drones. On any parsing or validation failure, an error
        is printed and the program exits.

        Raises:
            ValueError: If the CLI arguments are wrong, or a line fails
                to match its expected format (caught internally for
                most cases, but re-raised before the try block for the
                CLI argument check).
        """
        if len(sys.argv) != 2:
            raise ValueError("Ensure the config file is there")

        file = sys.argv[1]
        with open(file, mode="r") as f:
            data = f.readlines()

        lines: List[Tuple[int, str]] = []
        for i, line in enumerate(data):
            if "#" in line:
                line = line.split("#")[0]
            lines.append((i + 1, line.strip()))

        n_drones: Optional[int] = None
        start_hub: Optional[Zone] = None
        end_hub: Optional[Zone] = None
        valid_hubs: Set[str] = set()
        valid_connections: Set[Tuple[str, str]] = set()
        valid_coordinates: Set[Tuple[int, int]] = set()
        conn_name: Tuple = tuple()
        for row in lines:
            i, line = row

            if self.is_skippable(line):
                continue

            elif line.startswith("nb_drones"):
                if n_drones:
                    raise ValueError(f"line {i}: duplicated "
                                     "number of drones fild")
                n_drones_str = self.drones_num(row)
                n_drones = int(n_drones_str)
                if n_drones <= 0:
                    raise ValueError(f"line {i}: the number of drones must"
                                     " be a positive integer")
                self.nb_drones = int(n_drones)
            elif not n_drones:
                raise ValueError(f"line {i}: The first line must "
                                 "define the number of drones")

            elif line.startswith("start_hub"):
                if start_hub:
                    raise ValueError(f"line {i}: duplicate start zones")
                start_hub_fields = self.get_start(row)
                start_hub = self.validate_hub(start_hub_fields, i)
                start_hub.max_drones = n_drones
                self.validate_zones(start_hub, valid_hubs,
                                    valid_coordinates, i)
                self.start_zone = start_hub
                self.zones.update({start_hub.name: start_hub})

            elif line.startswith("hub"):
                hub_fields = self.get_hubs(row)
                hub = self.validate_hub(hub_fields, i)
                self.validate_zones(hub, valid_hubs,
                                    valid_coordinates, i)
                self.zones.update({hub.name: hub})

            elif line.startswith("end_hub"):
                if end_hub:
                    raise ValueError(f"line {i}: duplicated end zones")
                end_hub_fields = self.get_end(row)
                end_hub = self.validate_hub(end_hub_fields, i)
                self.validate_zones(end_hub, valid_hubs,
                                    valid_coordinates, i)
                end_hub.max_drones = n_drones
                self.end_zone = end_hub
                self.zones.update({end_hub.name: end_hub})

            elif line.startswith("connection"):
                connection = self.get_connection(row)
                name1, name2 = connection[0], connection[1]
                if name1 == name2:
                    raise ValueError(f"line {i}: a hub cannot connect "
                                     f"to itself '{name1}'")
                if name1 not in valid_hubs:
                    raise ValueError(f"line {i}: unknown hub '{name1}' "
                                     "in connection field")
                if name2 not in valid_hubs:
                    raise ValueError(f"line {i}: unknown hub '{name2}' "
                                     "in connection field")
                conn_name = tuple(sorted((name1, name2)))
                if conn_name in valid_connections:
                    raise ValueError(f"line {i}: duplicate connections!")

                self.connections.update({
                    conn_name: self.validate_connection(connection,
                                                        self.zones, i)})
                valid_connections.add(conn_name)
            else:
                raise ValueError(f"line {i}: invalid format '{line}'")

        self.is_there(n_drones, start_hub, end_hub, self.connections)
        self.validate_start_end(start_hub, end_hub)  # type: ignore
