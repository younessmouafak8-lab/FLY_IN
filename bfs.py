import heapq


def bfs(data, start, end):
    i = 1
    queue = []
    heapq.heappush(queue, (0, start.is_priority(), i, start))
    cheapest = {start: 0}
    parent = {start: None}
    path = []

    while queue:
        current_cost, ispriority, n, current = heapq.heappop(queue)
        if current_cost > cheapest[current]:
            continue
        if current == end:
            while current:
                path.append((current, cheapest[current]))
                current = parent[current]
            return path[::-1]

        for neighbor in data[current]:
            if neighbor.type == "blocked":
                continue
            cost = current_cost + neighbor.get_cost()
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
