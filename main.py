from parsing import Parse
from structure import Graph


def main():
    p = Parse()
    data = p.parse_file()
    if not data:
        return
    # print(data)
    zones = data["zones"]
    connections = data["connections"]
    # print(zones)
    # print(connections)
    graph = Graph(data["nb_drones"], data["start_zone"], data["end_zone"],
                  zones, connections)
    graph.build_list()


main()
