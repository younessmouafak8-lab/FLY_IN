from parsing import Parse
from structure import Graph, Drone
from simulation import Simulation
from algo import Algo


def main():
    p = Parse()
    data = p.parse_file()
    if not data:
        return
    zones = data["zones"]
    connections = data["connections"]

    graph = Graph(data["nb_drones"], data["start_zone"], data["end_zone"],
                  zones, connections)
    sim = Simulation(connections, zones)

    graph.build_list()

    algo = Algo(graph.graph, data["start_zone"], data["end_zone"], zones,
                connections)
    paths = algo.get_paths()
    if not paths:
        print("end is not connected to the start :(")
        exit(1)

    i = 0
    while i < data["nb_drones"]:

        if all([not p[0] for p in paths]):
            for j, p in enumerate(paths):
                paths[j] = (paths[j][1], paths[j][1], paths[j][2])

        for j, p in enumerate(paths):
            if not p[0]:
                continue

            paths[j] = (paths[j][0] - 1, paths[j][1], paths[j][2])

            drone = Drone(i + 1, p[2])
            sim.drones.append(drone)
            break

        i += 1
    sim.simulate()


try:
    main()
except Exception as e:
    print(f"Error: {e}")
