import sys
import re
from structure import Zone, Connection
import webcolors


class Parse:
    def __init__(self):
        self.nb_drones = {}
        self.start_zone = {}
        self.end_zone = {}
        self.zones = {}
        self.connections = {}

    def is_skippable(self, line):
        pattern = r"^\s*(#.*)?$"
        result = re.match(pattern, line)
        if not result:
            return False
        return True

    def drones_num(self, line: tuple):
        i, text = line
        pattern = r"^nb_drones: ([\-\+]?\d+)\s*(?:\s*#.*)?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid drones number field '{text}'")
        return result.group(1)

    def get_start(self, line):
        i, text = line
        pattern = (r"start_hub: ([^\-]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\w\-\+]+)(?:\s+(\w+=[\w\-\+]+))?"
                   r"(?:\s+(\w+=[\w\-\+]+))?\])?"
                   r"\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid start hub field {text}")
        return (result.groups())

    def get_hubs(self, line):
        i, text = line
        pattern = (r"hub: ([^\-]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\w\-\+]+)(?:\s+(\w+=[\w\-\+]+))?"
                   r"(?:\s+(\w+=[\w\-\+]+))?\])?"
                   r"\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid hub field {text}")
        return (result.groups())

    def get_end(self, line):
        i, text = line
        pattern = (r"end_hub: ([^\-]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=[\w\-\+]+)(?:\s+(\w+=[\w\-\+]+))?"
                   r"(?:\s+(\w+=[\w\-\+]+))?\])?"
                   r"\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid end hub field")
        return (result.groups())

    def get_connection(self, line):
        i, text = line
        pattern = (r"connection: ([\S]+)-([\S]+)"
                   r"(?:\s+\[max_link_capacity=([\-\+]?\d+)\])?\s*(?:#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid connection field '{text}'")
        return (result.groups())

    def is_there(self, nb, start, end, connections):
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

    def verify_metadata(self, hub, i):
        allowed_names = ("color", "max_drones", "zone")
        allowed_zones = ("normal", "blocked", "restricted", "priority")
        temp = set()
        data = {"type": "normal", "max_drones": 1, "color": "white"}
        for name in hub[3:]:
            if name:
                name = name.split("=")
                key = name[0]
                value = name[1]
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
                                         f" be a positive integer. {value}")
                if key == "color":
                    if not isinstance(value, str) or not value.isalpha():
                        raise ValueError(f"line {i}: color must be a string")
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

    def validate_connection(self, connection, hubs, i):
        con = {"zone1": hubs[connection[0]], "zone2": hubs[connection[1]]}
        val = {"max_link_capacity": 1}
        if connection[2]:
            num = int(connection[2])
            if num <= 0:
                raise ValueError(f"line {i}: max_link_capacity must be a "
                                 "positive integer.")
            val["max_link_capacity"] = num
        con.update(val)
        return Connection(**con)

    def validate_zones(self, zone, valid_zones, valid_coordinates, i):
        if zone.name in valid_zones:
            raise ValueError(f"line {i}: duplicate zone names are "
                             f"not tolerated '{zone.name}'")
        valid_zones.add(zone.name)
        if zone.coordinates in valid_coordinates:
            raise ValueError(f"Line {i}: duplicated "
                             "coordinates")
        valid_coordinates.add(zone.coordinates)

    def validate_start_end(self, start, end):
        if start.type == 'blocked':
            raise ValueError("start zone cant be blocked")
        if end.type == 'blocked':
            raise ValueError("end zone cant be blocked")

    def parse_file(self):
        if len(sys.argv) != 2:
            raise ValueError("Ensure the config file is there")
        file = sys.argv[1]
        with open(file, mode="r") as f:
            data = f.readlines()
        lines = []
        for i, line in enumerate(data):
            lines.append((i + 1, line))
        n_drones = None
        start_hub = None
        end_hub = None
        valid_hubs = set()
        valid_connections = set()
        valid_coordinates = set()
        try:
            for row in lines:
                i, line = row

                if self.is_skippable(line):
                    continue

                elif line.startswith("nb_drones"):
                    if n_drones:
                        raise ValueError(f"line {i}: duplicated "
                                         "number of drones fild")
                    n_drones = self.drones_num(row)
                    n_drones = int(n_drones)
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
                    start_hub = self.get_start(row)
                    start_hub = self.validate_hub(start_hub, i)
                    start_hub.max_drones = n_drones
                    self.validate_zones(start_hub, valid_hubs,
                                        valid_coordinates, i)
                    self.start_zone = start_hub
                    self.zones.update({start_hub.name: start_hub})

                elif line.startswith("hub"):
                    hub = self.get_hubs(row)
                    hub = self.validate_hub(hub, i)
                    self.validate_zones(hub, valid_hubs,
                                        valid_coordinates, i)
                    self.zones.update({hub.name: hub})

                elif line.startswith("end_hub"):
                    if end_hub:
                        raise ValueError(f"line {i}: duplicated end zones")
                    end_hub = self.get_end(row)
                    end_hub = self.validate_hub(end_hub, i)
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
                    valid_connections.add(tuple(sorted((name1, name2))))
                else:
                    raise ValueError(f"line {i}: invalid format '{line}'")

            self.is_there(n_drones, start_hub, end_hub, self.connections)
            self.validate_start_end(start_hub, end_hub)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            exit(1)
        except PermissionError:
            print("Error: permission denied")
            exit(1)
        except ValueError as er:
            print(f"Error: {er}")
            exit(1)
