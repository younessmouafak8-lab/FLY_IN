from parsing import Parse
from structure import Graph
from simulation import Simulation
from algo import Algo


class Main:
    def __init__(self):
        self.parser = Parse()
        self.graph = None
        self.sim = None
        self.algo = None

    def run(self):
        self.parser.parse_file()

        self.graph = Graph(self.parser.nb_drones, self.parser.start_zone,
                           self.parser.end_zone, self.parser.zones,
                           self.parser.connections)

        self.graph.build_list()

        algo = Algo(self.graph.graph, self.parser.start_zone,
                    self.parser.end_zone, self.parser.zones,
                    self.parser.connections)
        paths = algo.get_paths()
        if not paths:
            print("end is not connected to the start :(")
            exit(1)

        self.sim = Simulation(self.parser.nb_drones, self.parser.connections,
                              self.parser.zones, paths)

        self.sim.distribute_paths()
        self.sim.simulate()


main = Main()
main.run()
