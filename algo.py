import heapq


class Algo:

    def __init__(self, data, start, end, zones, connections):
        self.data = data
        self.start = start
        self.end = end
        self.zones = zones
        self.connections = connections

    def custom_dijkstra(self):
        i = 1
        queue = []
        start = self.start
        heapq.heappush(queue, (0, start.is_priority(), i, start))
        cheapest = {start: 0}
        parent = {start: None}
        path = []

        while queue:
            current_cost, ispriority, n, current = heapq.heappop(queue)
            if current_cost > cheapest[current]:
                continue
            if current == self.end:
                while current:
                    path.append((current))
                    current.usage += 0.01
                    current = parent[current]
                return path[::-1]

            for neighbor in self.data[current]:
                if neighbor.type == "blocked":
                    continue
                cost = current_cost + neighbor.get_cost() + neighbor.usage
                if neighbor not in cheapest:
                    cheapest[neighbor] = cost
                    heapq.heappush(queue, (cost, neighbor.is_priority(), i,
                                           neighbor))
                    parent[neighbor] = current
                else:
                    saved_cost = cheapest[neighbor]
                    if cost < saved_cost:
                        cheapest[neighbor] = cost
                        heapq.heappush(queue, (cost, neighbor.is_priority(), i,
                                               neighbor))
                        parent[neighbor] = current
                i += 1

    def get_path(self):
        return self.custom_dijkstra()

    def get_con_cost(self, connections, p):
        return connections[tuple(sorted((p[0].name, p[1].name)))].max_link_capacity

    def get_max(self, cnx, p):
        return cnx if cnx < p[1].max_drones else p[1].max_drones

    def get_paths(self):
        paths = []
        path = self.get_path()
        while path not in paths:
            paths.append(path)
            path = self.get_path()
        paths = [(self.get_max(self.get_con_cost(self.connections, p), p),
                 self.get_max(self.get_con_cost(self.connections, p), p), p)
                 for p in paths]
        return paths
