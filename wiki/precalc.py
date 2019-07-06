from GraphReader import _int_to_bytes, GraphReader
from random import shuffle, randrange
from time import time

start_time = time()

reader = GraphReader('data/offset', 'data/edges')

N = 5054753
dist = [-1 for i in range(N)]
go_to = [[] for i in range(N)]
order = list(range(N))
shuffle(order)

for start_page_id in order:
    if dist[start_page_id] != -1:
        continue
    queue = [start_page_id]
    idx = 0
    dist[start_page_id] = 0
    while idx < len(queue):
        cur_vertex = queue[idx]
        #print(cur_vertex)
        idx += 1
        edges = reader.Edges(cur_vertex)
        for next_ in edges:
            if dist[next_] == -1:
                dist[next_] = dist[cur_vertex] + 1
                queue.append(next_)
                go_to[next_].append(cur_vertex)

easy_pairs = []
medium_pairs = []
hard_pairs = []

NONE = 2**32 - 1

dists = [[3, 4], [5, 7], [8, 11]]
for cur_vertex in range(N):
    v = cur_vertex
    if v % 10000 == 0:
        print(v, 'ready')
    visited = []
    max_steps = randrange(dists[2][0], dists[2][1])
    while len(visited) < max_steps:
        if len(go_to[v]) == 0:
            break
        next_ = go_to[randrange(0, len(go_to[v]) - 1)]
        visited.append(next_)
    easy_steps = min(randrange(dists[0][0], dists[0][1]), len(visited))
    medium_steps = min(randrange(dists[1][0], dists[1][1]), len(visited))
    hard_steps = min(randrange(dists[2][0], dists[2][1]), len(visited))
    if easy_steps >= dists[0][0]:
        easy_steps.append([cur_vertex, visited[easy_steps - 1]])
    if medium_steps >= dists[1][0]:
        medium_steps.append([cur_vertex, visited[medium_steps - 1]])
    if hard_steps >= dists[2][0]:
        hard_steps.append([cur_vertex, visited[hard_steps - 1]])

hard = open('data/hard', 'wb')
hard.write(_int_to_bytes(len(hard_pairs)))
for p in hard_pairs:
    hard.write(_int_to_bytes(p[0]))
    hard.write(_int_to_bytes(p[1]))
hard.close()

medium = open('data/medium', 'wb')
medium.write(_int_to_bytes(len(medium_pairs)))
for p in medium_pairs:
    medium.write(_int_to_bytes(p[0]))
    medium.write(_int_to_bytes(p[1]))
medium.close()

easy = open('data/easy', 'wb')
easy.write(_int_to_bytes(len(easy_pairs)))
for p in easy_pairs:
    easy.write(_int_to_bytes(p[0]))
    easy.write(_int_to_bytes(p[1]))
easy.close()

print(time() - start_time)
