import sys
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from structure import Zone, Connection
import webcolors  # type: ignore


class Parse:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start_zone: Zone
        self.end_zone: Zone
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[Tuple[str, str], Connection] = {}

    def is_skippable(self, line: str) -> bool:
        pattern = r"^\s*(#.*)?$"
        result = re.match(pattern, line)
        if not result:
            return False
        return True

    def drones_num(self, line: Tuple[int, str]) -> str:
        i, text = line
        pattern = r"nb_drones: ([\-\+]?\d+)\s*(?:\s*#.*)?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid drones number field '{text}'")
        return result.group(1)

    def get_start(self, line: Tuple[int, str]) -> Tuple[Optional[str], ...]:
        i, text = line
        pattern = (r"start_hub: ([^\-\s]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\S]+)(?:\s+(\w+=[\S]+))?"
                   r"(?:\s+(\w+=[\S]+))?\])?"
                   r"\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid start hub field {text}")
        return (result.groups())

    def get_hubs(self, line: Tuple[int, str]) -> Tuple[Optional[str], ...]:
        i, text = line
        pattern = (r"hub: ([^\-\s]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\S]+)(?:\s+(\w+=[\S]+))?"
                   r"(?:\s+(\w+=[\S]+))?\])?"
                   r"\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid hub field {text}")
        return (result.groups())

    def get_end(self, line: Tuple[int, str]) -> Tuple[Optional[str], ...]:
        i, text = line
        pattern = (r"end_hub: ([^\-\s]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\S]+)(?:\s+(\w+=[\S]+))?"
                   r"(?:\s+(\w+=[\S]+))?\])?"
                   r"\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid end hub field")
        return (result.groups())

    def get_connection(self, line: Tuple[int, str]
                       ) -> Tuple[Optional[str], ...]:
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

    def validate_hub(self, hub, i):
        values = {"name": hub[0],
                  "coordinates": (int(hub[1]), int(hub[2]))}
        values.update(self.verify_metadata(hub, i))
        return Zone(**values)

    def validate_connection(self, connection: Tuple[Optional[str], ...],
                            hubs: Dict[str, Zone], i: int) -> Connection:
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
        if zone.name in valid_zones:
            raise ValueError(f"line {i}: duplicate zone names are "
                             f"not tolerated '{zone.name}'")
        valid_zones.add(zone.name)
        if zone.coordinates in valid_coordinates:
            raise ValueError(f"Line {i}: duplicated "
                             "coordinates")
        valid_coordinates.add(zone.coordinates)

    def validate_start_end(self, start: Zone, end: Zone) -> None:
        if start.type == 'blocked':
            raise ValueError("start zone cant be blocked")
        if end.type == 'blocked':
            raise ValueError("end zone cant be blocked")

    def parse_file(self) -> None:
        if len(sys.argv) != 2:
            raise ValueError("Ensure the config file is there")
        file = sys.argv[1]
        with open(file, mode="r") as f:
            data = f.readlines()
        lines: List[Tuple[int, str]] = []
        for i, line in enumerate(data):
            lines.append((i + 1, line.strip()))
        n_drones: Optional[int] = None
        start_hub: Optional[Zone] = None
        end_hub: Optional[Zone] = None
        valid_hubs: Set[str] = set()
        valid_connections: Set[Tuple[str, str]] = set()
        valid_coordinates: Set[Tuple[int, int]] = set()
        conn_name: Tuple = tuple()
        try:
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
        except FileNotFoundError as e:
            print(f"Error: {e}")
            exit(1)
        except PermissionError:
            print("Error: permission denied")
            exit(1)
        except ValueError as er:
            print(f"Error: {er}")
            exit(1)