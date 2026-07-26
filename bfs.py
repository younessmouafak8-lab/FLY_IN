from collections import deque

graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}
# Find shortest path from 1 to 5
# Expected: 3 (path: 1 -> 2 -> 4 -> 5, or 1 -> 3 -> 4 -> 5)


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


print(bfs(graph, "A", "E"))
