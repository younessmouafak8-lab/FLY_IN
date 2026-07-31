from collections import deque

graph = {
    'roof.1': ['start', 'waypoint2'],
    'waypoint2': ['roof.1', 'goal'],
    'start': ['roof.1'],
    'goal': ['waypoint2']}


def bfs(data, start, end):
    t_queue = deque([start])
    visited = [start]
    path = []
    parent = {start: None}

    while t_queue:
        current = t_queue.popleft()
        if current == end:
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]
        for neighbor in data[current]:
            if neighbor not in visited:
                t_queue.append(neighbor)
                parent[neighbor] = current
                visited.append(neighbor)

    return visited


print(bfs(graph, "start", "end"))
