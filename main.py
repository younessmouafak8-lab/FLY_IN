from parsing import Parse
from structure import Graph
from simulation import Simulation
from algo import Algo
from typing import Optional


class Main:
    """Wires together parsing, pathfinding, and simulation for one run.

    Parses the map file given on the command line, builds the zone
    graph, finds candidate paths from start to end, distributes those
    paths across all drones, and runs the turn-by-turn simulation.

    Attributes:
        parser: The Parse instance used to read and validate the map
            file.
        graph: The built Graph, or None until run() constructs it.
        sim: The Simulation instance, or None until run() constructs it.
        algo: The Algo instance, or None until run() constructs it.
    """

    def __init__(self) -> None:
        """Initializes Main with a fresh parser and no graph/sim/algo yet."""
        self.parser = Parse()
        self.graph: Optional[Graph] = None
        self.sim: Optional[Simulation] = None
        self.algo: Optional[Algo] = None

    def run(self) -> None:
        """Runs the full pipeline: parse, build graph, find paths, simulate.

        Exits the program with an error message if no path exists
        between the start and end zones.
        """
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
try:
    main.run()
except Exception as err:
    print(f"Error: {err}")
    exit(1)
