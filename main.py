from parsing import Parse
from structure import Graph, Drone
from simulation import Simulation


def main():
    p = Parse()
    data = p.parse_file()
    if not data:
        return
    zones = data["zones"]
    connections = data["connections"]
    graph = Graph(data["nb_drones"], data["start_zone"], data["end_zone"],
                  zones, connections)
    graph.build_list()
    sim = Simulation(connections, zones)
    for i in range(data["nb_drones"]):
        drone = Drone(i + 1, graph.get_path())
        sim.drones.append(drone)
    sim.simulate()


main()
