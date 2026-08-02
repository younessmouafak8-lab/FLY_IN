class Simulation:
    def __init__(self):
        self.drones = []
        self.zone_usage = {}
        self.link_usage = {}
        self.all_done = False
        self.turn = 0

    def check_drones(self):
        return all([drone.done for drone in self.drones])

    def simulate(self):
        while not self.all_done:

            for drone in self.drones:
                zone, cost = drone.path[drone.i]
                if drone.i >= len(drone.path) - 1:
                    drone.done = True
                    continue

                drone.i += 1
            if self.check_drones():
                self.all_done = True

            self.turn += 1
