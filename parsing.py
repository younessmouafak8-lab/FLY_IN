import sys
import re
from structure import Zone, Connection


class Parse:

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
                   r"(?:\s+\[(\w+=\w+)(?:\s+(\w+=\w+))?(?:\s+(\w+=\w+))?\])?"
                   r"(?:\s*#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid start hub field {text}")
        return (result.groups())

    def get_hubs(self, line):
        i, text = line
        pattern = (r"hub: ([^\-]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=\w+)(?:\s+(\w+=\w+))?(?:\s+(\w+=\w+))?\])?"
                   r"(?:\s*#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid hub field {text}")
        return (result.groups())

    def get_end(self, line):
        i, text = line
        pattern = (r"end_hub: ([^\-]+)\s+([\-\+]?\d+)\s+([\-\+]?\d+)"
                   r"(?:\s+\[(\w+=\w+)(?:\s+(\w+=\w+))?(?:\s+(\w+=\w+))?\])?"
                   r"(?:\s*#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid end hub field")
        return (result.groups())

    def get_connection(self, line):
        i, text = line
        pattern = (r"connection: ([\S]+)-([\S]+)"
                   r"(?:\s+\[max_link_capacity=([\-\+]?\d+)\])?(?:\s*#.*)?$")
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"line {i}: invalid connection field '{text}'")
        return (result.groups())

    def is_there(self, nb, start, hubs, end, connections):
        if not nb:
            raise ValueError("You must provide the number of drones!\n")
        if not start:
            raise ValueError("You must provide a start hub!, start_hub: <name>"
                             " <x> <y> [metadata]")
        if not end:
            raise ValueError("You must provide a end hub!, end_hub: <name> <x>"
                             " <y> [metadata]")
        if not hubs:
            raise ValueError("You must provide hubs!, hub: <name> <x> <y>"
                             " [metadata]")
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
                    if not isinstance(value, str):
                        raise ValueError(f"line {i}: color must be a string")
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

    def validate_start_end(self, start, end):
        if (start.coordinates == end.coordinates):
            raise ValueError("start and end zones have "
                             "the same coordinates")
        if start.type == 'blocked':
            raise ValueError("start zone cant be blocked")
        if end.type == 'blocked':
            raise ValueError("end zone cant be blocked")

    def parse_file(self):
        if len(sys.argv) != 2:
            raise ValueError("The config file is required")
        file = sys.argv[1]
        with open(file, mode="r") as f:
            data = f.readlines()
        lines = []
        for i, line in enumerate(data):
            lines.append((i + 1, line))
        values = {}
        n_drones = None
        start_hub = None
        hubs = {}
        end_hub = None
        connections = {}
        valid_hubs = set()
        valid_connections = set()
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
                    values.update({"nb_drones": int(n_drones)})
                elif not n_drones:
                    raise ValueError(f"line {i}: The first line must "
                                     "define the number of drones")

                elif line.startswith("start_hub"):
                    if start_hub:
                        raise ValueError(f"line {i}: duplicate start zones")
                    start_hub = self.get_start(row)
                    if start_hub[0] in valid_hubs:
                        raise ValueError(f"line {i}: duplicate zone names "
                                         f"are not tolerated '{start_hub[0]}'")
                    start_hub = self.validate_hub(start_hub, i)
                    valid_hubs.add(start_hub.name)
                    values.update({"start_zone": start_hub})
                    hubs.update({start_hub.name: start_hub})

                elif line.startswith("hub"):
                    hub = self.get_hubs(row)
                    if hub[0] in valid_hubs:
                        raise ValueError(f"line {i}: duplicate zone names "
                                         f"are not tolerated '{hub[0]}'")
                    hubs.update({hub[0]: self.validate_hub(hub, i)})
                    valid_hubs.add(hub[0])

                elif line.startswith("end_hub"):
                    if end_hub:
                        raise ValueError(f"line {i}: duplicated end zones")
                    end_hub = self.get_end(row)
                    if end_hub[0] in valid_hubs:
                        raise ValueError(f"line {i}: duplicate zone names "
                                         f"are not tolerated '{end_hub[0]}'")
                    end_hub = self.validate_hub(end_hub, i)
                    valid_hubs.add(end_hub.name)
                    values.update({"end_zone": end_hub})
                    hubs.update({end_hub.name: end_hub})

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

                    connections.update({conn_name:
                                        self.validate_connection(connection,
                                                                 hubs, i)})
                    valid_connections.add(tuple(sorted((name1, name2))))
                else:
                    raise ValueError(f"line {i}: invalid format '{line}'")

            self.is_there(n_drones, start_hub, hubs, end_hub, connections)
            values.update({"zones": hubs})
            values.update({"connections": connections})
            self.validate_start_end(start_hub, end_hub)
            return values
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except PermissionError:
            print("Error: permission denied")
        except ValueError as er:
            print(f"Error: {er}")
