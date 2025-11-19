# Problem Statement

# You are given n cities numbered from 0 to n-1 and a list of bidirectional roads, where each road connects two cities.

# You start in city 0.
# Visiting each city requires fuel cost = 1 per road traveled.

# You must visit all cities at least once (in any order).
# Compute the minimum total fuel required to visit all cities starting from 0.

# Input

# n: number of cities

# roads: list of [u, v] pairs meaning a bidirectional road between u and v

# Rules

# All cities are guaranteed to be reachable from city 0.

# You may revisit cities if needed, but fuel is spent each time.

# Output

# Minimum total fuel required.

import queue


roads = [
    [0, 1],
    [0, 2],
    [1, 3],
    [1, 4]
]

def cost(n, roads):
    from collections import defaultdict, deque
    
    # Build bidirectional graph
    graph = defaultdict(list)
    for i, j in roads:
        graph[i].append(j)
        graph[j].append(i)
    
    # For a tree structure: minimum cost = 2*(n-1) - max_depth_from_0
    # This is because we traverse each edge twice (going and returning)
    # except the path to the deepest node (which we traverse once)
    
    # Find maximum depth from city 0 using BFS
    dq = deque()
    dq.append((0, 0))  # (city, depth)
    visited = set()
    visited.add(0)
    max_depth = 0
    
    while dq:
        city, depth = dq.popleft()
        max_depth = max(max_depth, depth)
        print(depth, max_depth)
        
        for neighbor in graph[city]:
            if neighbor not in visited:
                visited.add(neighbor)
                dq.append((neighbor, depth + 1))
    
    # If it's a tree (n-1 edges for n nodes), use the formula
    # Otherwise, we need a different approach
    num_edges = len(roads)
    if num_edges == n - 1:  # It's a tree
        return 2 * (n - 1) - max_depth
    else:
        # For general graphs, we need to find minimum spanning tree
        # or use a different algorithm. For now, return a conservative estimate.
        # In practice, you'd use DFS to find a spanning tree and calculate cost.
        return 2 * (n - 1) - max_depth  # Approximation

#print( cost(5, roads) )


def cost_dist(n, cities):
    from collections import defaultdict, deque

    graph = defaultdict(list)

    for u, v in cities:
        graph[u].append(v)
        graph[v].append(u)

    dist = [-1] * n
    #dist[0] = 0

    dq = deque([0])
    while dq:
        city = dq.popleft()
        for nei in graph[city]:
            if dist[nei] == -1:
                dist[nei] = dist[city] + 1
                dq.append(nei)
    
    print(dist)


print(cost_dist(5, roads))