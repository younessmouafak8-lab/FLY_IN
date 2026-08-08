from parsing import Parse
from structure import Graph
from simulation import Simulation
from algo import Algo
from typing import Optional


class Main:
    def __init__(self) -> None:
        self.parser = Parse()
        self.graph: Optional[Graph] = None
        self.sim: Optional[Simulation] = None
        self.algo: Optional[Algo] = None

    def run(self) -> None:
        self.parser.parse_file()
        start_zone = self.parser.start_zone
        end_zone = self.parser.end_zone

        self.graph = Graph(self.parser.nb_drones, start_zone,
                           end_zone, self.parser.zones,
                           self.parser.connections)

        self.graph.build_list()

        algo = Algo(self.graph.graph, start_zone,
                    end_zone, self.parser.zones,
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