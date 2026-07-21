import sys
import re


class Parse:

    # def is_skippable(self, text):
    #         pattern = r"\s+#"
    #     result = re.match(pattern, text)
    #     if not result:
    #         return False
    #     return result.group(1)

    def drones_num(self, text: str):
        pattern = r"^nb_drones: (\d+)\s*$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError(f"invalid drones number field '{text}'")
        return result.group(1)


    def get_start(self, text):
        # [color=green]
        pattern = r"start_hub: ([a-z]+)\s+(\d+)\s*(\d+)(?:\s+\[(.*?)\]\s*)?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError("invalid start hub field")
        return (result.group(1), result.group(2), result.group(3), result.group(4))

    def get_hubs(self, text):
        pattern = r"hub: (\w+)\s+(\d+)\s*(\d+)(?:\s+\[(.*?)\]\s*)?$"
        result = re.match(pattern, text)
        if not result:
            raise ValueError("invalid hub field")
        return (result.group(1), result.group(2), result.group(3), result.group(4))

    def parse_file(self):
        if len(sys.argv) != 2:
            raise ValueError("The config file is required")
        file = sys.argv[1]
        with open(file, mode="r") as f:
            data = f.readlines()
        hubs = []
        try:
            for line in data:
                if line.startswith('#'):
                    continue
                elif line.startswith("nb_drones"):
                    n_drones = self.drones_num(line)
                elif line.startswith("start_hub"):
                    start_hub = self.get_start(line)
                elif line.startswith("hub"):
                    hubs.append(self.get_hubs(line))

            print(n_drones)
            print(start_hub)
            print(hubs)

        except ValueError as er:
            print(f"Error: {er}")


p = Parse()
p.parse_file()
