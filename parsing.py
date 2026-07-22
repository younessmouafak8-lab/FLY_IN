import sys
import re


class Parse:

    def is_skippable(self, text):
        pattern = r"^\s*(#.*)?$"
        result = re.match(pattern, text)
        if not result:
            return False
        return True

    def drones_num(self, text: str):
        pattern = r"^nb_drones: (\d+)\s*$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"invalid drones number field '{text}'")
        return result.group(1)

    def get_start(self, text):
        # [color=green]
        pattern = r"start_hub: (\w+)\s*(\d+)\s*(\d+)(?:\s+\[(\w+=\w+)(?:\s+(\w+=\w+))?(?:\s+(\w+=\w+))?\])?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"invalid start hub field {text}")
        return (result.groups())

    def get_hubs(self, text):
        pattern = r"hub: (\w+)\s+(\d+)\s+(\d+)(?:\s+\[(\w+=\w+)(?:\s+(\w+=\w+))?(?:\s+(\w+=\w+))?\])?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"invalid hub field {text}")
        return (result.groups())

    def get_end(self, text):
        pattern = r"end_hub: (\w+)\s*(\d+)\s*(\d+)(?:\s+\[(\w+=\w+)(?:\s+(\w+=\w+))?(?:\s+(\w+=\w+))?\])?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError("invalid end hub field")
        return (result.groups())

    def get_connection(self, text):
        pattern = r"connection: (\w+)-(\w+)(?:\s+\[(max_link_capacity=\d+)\])?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"invalid connection field {text}")
        return (result.groups())

    def is_there(self, nb, start, hubs, end, connections):
        if not nb:
            raise ValueError("You must provide the number of drones!\n")
        if not start:
            raise ValueError("You must provide a start hub!, start_hub: <name> <x> <y> [metadata]")
        if not end:
            raise ValueError("You must provide a end hub!, end_hub: <name> <x> <y> [metadata]")
        if not hubs:
            raise ValueError("You must provide hubs!, hub: <name> <x> <y> [metadata]")
        if not connections:
            raise ValueError("You must provide connections!, connection: <name1>-<name2> [metadata]")

    def verify_metadata(self, hub):
        allowed_names = ("color", "max_drones", "zone")
        allowed_zones = ("normal", "blocked", "restricted", "priority")
        temp = set()
        data = {}
        for name in hub[3:]:
            if name:
                name = name.split("=")
                key = name[0]
                value = name[1]
                if key not in temp and key in allowed_names:
                    temp.add(key)
                else:
                    raise ValueError(f"invalid name {key}")
                if key == "zone":
                    if value not in allowed_zones:
                        raise ValueError(f"invalid zone type {key}:{value}")
                    data.update({key: value})
                if key == "max_drones":
                    if not value.isdigit():
                        raise ValueError("value for max_drones must be a positive integer.")
                    value = int(value)
                    data.update({key: value})
                if key == "color":
                    if not isinstance(value, str):
                        raise ValueError("color must be a string")
                    data.update({key: value})
        return data

    def parse_file(self):
        if len(sys.argv) != 2:
            raise ValueError("The config file is required")
        file = sys.argv[1]
        with open(file, mode="r") as f:
            data = f.readlines()
        values = {}
        n_drones = None
        start_hub = None
        hubs = []
        end_hub = None
        connections = []
        valid_hubs = set()
        # valid_hubs = set()
        try:
            for line in data:
                # print(line.re, end="")
                if self.is_skippable(line):
                    continue
                elif line.startswith("nb_drones") and not n_drones:
                    n_drones = self.drones_num(line)
                elif not n_drones:
                    raise ValueError("The first line must define the number of drones")
                elif line.startswith("start_hub") and not start_hub:
                    start_hub = self.get_start(line)
                    if start_hub[0] in valid_hubs:
                        raise ValueError(f"duplicate zone names are not tolerated '{start_hub[0]}'")
                    valid_hubs.add(start_hub[0])
                elif line.startswith("hub"):
                    hub = self.get_hubs(line)
                    if hub[0] in valid_hubs:
                        raise ValueError(f"duplicate zone names are not tolerated '{hub[0]}'")
                    hubs.append(hub)
                    valid_hubs.add(hub[0])
                elif line.startswith("end_hub") and not end_hub:
                    end_hub = self.get_end(line)
                    if end_hub[0] in valid_hubs:
                        raise ValueError(f"duplicate zone names are not tolerated '{end_hub[0]}'")
                    valid_hubs.add(end_hub[0])
                elif line.startswith("connection"):
                    connection = self.get_connection(line)
                    name1, name2 = connection[0], connection[1]
                    if name1 == name2:
                        raise ValueError(f"a hub cannot connect to itself '{name1}'")
                    if name1 not in valid_hubs:
                        raise ValueError(f"unknown hub '{name1}' in connection field")
                    if name2 not in valid_hubs:
                        raise ValueError(f"unknown hub '{name2}' in connection field")
                    connections.append(connection)
                else:
                    raise ValueError(f"invalid format '{line}'")

            self.is_there(n_drones, start_hub, hubs, end_hub, connections)
            values.update({"nb_drones": int(n_drones)})
            print(start_hub)
            values.update({"start_zone": {"name": start_hub[0],
                                          "x": int(start_hub[1]),
                                          "y": int(start_hub[2]),
                                          "metadata":
                                          self.verify_metadata(start_hub)}})
            # print(end_hub)
            print(hubs)
            print(connections)
        except ValueError as er:
            print(f"Error: {er}")


p = Parse()
p.parse_file()
