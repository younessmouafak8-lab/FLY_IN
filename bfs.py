import heapq


def bfs(data, start, end):
    i = 0
    queue = []
    heapq.heappush(queue, (start.get_cost(), start.is_priority(), i, start))
    cheapest = {start: 0}
    parent = {start: None}
    path = []

    while queue:
        current_cost, ispriority, n, current = heapq.heappop(queue)
        if current == end:
            while current:
                path.append(current.name)
                current = parent[current]
            return path[::-1]

        for neighbor in data[current]:
            cost = current_cost + neighbor.get_cost()
            if neighbor not in cheapest and neighbor.type != "blocked":
                cheapest[neighbor] = cost
                heapq.heappush(queue, (cost, neighbor.is_priority(), i, neighbor))
                parent[neighbor] = current
            elif neighbor.get_cost():
                saved_cost = cheapest[neighbor]
                if cost < saved_cost:
                    cheapest[neighbor] = cost
                    heapq.heappush(queue, (cost, neighbor.is_priority(), i, neighbor))
                    parent[neighbor] = current
            i += 1
