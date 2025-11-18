grid = [[0,0,0],[0,2,0],[0,0,0],[0,0,0],[0,0,0]]
start = (0,0)
end = (2,2)

def bfs_no_dist_array(grid, start, end):
    # we're just looking for the shortest path to end
    dirs = [(0,1), (0,-1), (1,0), (-1, 0)]
    start = [i for i in start]
    start.append(0)
    from collections import deque
    dq = deque()
    dq.append(start)

    visited = set()
    
    while dq:
        r, c, steps = dq.popleft()
        if (r, c) == end:
            return steps
        for dx, dy in dirs:
            nr, nc = r + dx, c + dy
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if not grid[nr][nc] == 1 and not (nr, nc) in visited:
                    visited.add((nr, nc))
                    dq.append([nr, nc, steps + 1])


#print( bfs_no_dist_array(grid, start, end) )

def bfs_with_dist_array(grid, start):
    dirs = [(0,1), (0,-1), (1,0), (-1, 0)]
    from collections import deque
    dq = deque()
    dq.append(start)
    dist = [[-1] * len(grid[0]) for _ in range(len(grid))]
    dist[start[0]][start[1]] = 0

    while dq:
        r, c = dq.popleft()
        for dx, dy in dirs:
            nr, nc = r + dx, c + dy
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if not grid[nr][nc] == 1 and dist[nr][nc] == -1:
                    dq.append([nr, nc])
                    dist[nr][nc] = dist[r][c] + 1

    return dist
e1,e2 = end
#print(bfs_with_dist_array(grid, start)[e1][e2])

o2 = 2
start = (0, 0, 2)
def bfs_with_dist_array_o2(grid, start):
    dirs = [(0,1), (0,-1), (1,0), (-1, 0)]
    from collections import deque
    dq = deque()
    dq.append(start)
    dist = [[-1] * len(grid[0]) for _ in range(len(grid))]
    dist[start[0]][start[1]] = 0

    while dq:
        r, c, o2 = dq.popleft()
        #print(r, c, o2)
        if o2 > 0:
            o2 -= 1
            for dx, dy in dirs:
                nr, nc = r + dx, c + dy
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    if not grid[nr][nc] == 1 and dist[nr][nc] == -1:
                        if grid[nr][nc] == 2:
                            o2 += 2
                        dq.append([nr, nc, o2])
                        dist[nr][nc] = dist[r][c] + 1

    #print(dist)

    return dist

#for i in bfs_with_dist_array_o2(grid, start): print(i, end='\n')

from collections import defaultdict
from turtle import teleport
graph = defaultdict(list)
graph[1].append(2)
graph[2].append(1)

graph[2].append(3)
graph[3].append(2)

# for k, v in graph.items():
#     print(k, v)

grid = [[0, 2, 1, 0],[0, 0, 0, 2],[1, 0, 1, 0],[2, 0, 0, 0]]
print('maze')
def teleport_maze(grid_):

    grid = [[0, 2, 1, 0],[0, 0, 0, 2],[1, 0, 1, 0],[2, 0, 0, 0]] if not grid_ else grid_
    rs, cs = (0, 0)
    re, ce = (4, 4)
    dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    visited = set()

    steps = 0
    from collections import deque
    dq = deque()
    dq.append([rs, cs, steps])
    teleport = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 2:
                teleport.append((i, j))

    #print(teleport)

    while dq:
        r, c, steps = dq.popleft()
        #print(r, c, steps)
        if (r, c) == (re, ce):
            #print('stets')
            return steps
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if not grid[nr][nc] == 1 and not (nr, nc) in visited:
                    if grid[nr][nc] == 0:
                        visited.add((nr, nc))
                        dq.append((nr, nc, steps + 1))
                    elif grid[nr][nc] == 2 and not (nr, nc) in visited:
                        for x in teleport:
                            if x not in visited:
                                visited.add(x)
                                j = [i for i in x]
                                j.append(steps + 1 )
                                dq.append(j)


    return -1


def teleport_maze_defaultdict(grid_, end):

    grid = [[0, 2, 1, 0],[0, 0, 0, 2],[1, 0, 1, 0],[2, 0, 0, 0]] if not grid_ else grid_
    start = (0, 0)
    re, ce = (3, 3) if not end else end
    dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    from collections import defaultdict
    graph = defaultdict(list)
    teleports = []

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 0 or grid[i][j] == 2:
                for dr, dc in dirs:
                    nr, nc = dr + i, dc + j
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != 1:
                        graph[(i,j)].append((nr, nc))
                        

                    if grid[i][j] == 2 and not (i,j) in teleports:
                        teleports.append((i,j))
    
    # add zero‑cost edges between teleport cells
    for i in range(len(teleports)):
        for j in range(i+1, len(teleports)):
            graph[teleports[i]].append(teleports[j])
            graph[teleports[j]].append(teleports[i])

    #for k,v in graph.items(): print(k, v, end='\n')

    from collections import deque
    dq = deque([start])
    tele_set = set(teleports)
    dist = {start: 0}

    while dq:
        r, c = dq.popleft()
        steps = dist[(r, c)]
        if (r, c) == (re, ce):
            return steps
        for nr, nc in graph[(r, c)]:
            cost = 0 if (r, c) in tele_set and (nr, nc) in tele_set else 1
            new_steps = steps + cost
            if new_steps < dist.get((nr, nc), float('inf')):
                dist[(nr, nc)] = new_steps
                if cost == 0:
                    dq.appendleft((nr, nc))
                else:
                    dq.append((nr, nc))

    return -1

grid1 = [
    [0, 1, 2],
    [0, 1, 0],
    [2, 1, 0] # 4
]

grid2 = [
    [0, 1, 0, 0, 0],
    [2, 1, 1, 1, 2],
    [0, 0, 0, 0, 0] # 4
]

grid3 = [
    [0, 2, 0],
    [2, 1, 2],
    [0, 2, 0] # 2
]

#print(teleport_maze(grid))
print(teleport_maze_defaultdict(grid2, end=(2,2)))

