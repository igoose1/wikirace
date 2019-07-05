from GraphReader import _int_to_bytes, GraphReader
from random import shuffle, randrange
from time import time

start_time = time()

reader = GraphReader('data/reverse_offset', 'data/reverse_edges')

N = 5054753
dist = [-1 for i in range(N)]
go_to = [-1 for i in range(N)]
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
                go_to[next_] = cur_vertex


reader = GraphReader('data/offset', 'data/edges')
out = open('data/good_end_0', 'wb')

NONE = 2**32 - 1
good_end = [-1 for i in range(N)]

def find_good_ends(min_dist, max_dist):
    for cur_vertex in range(N):
        made_steps = 0
        steps = randrange(min_dist, max_dist)
        v = cur_vertex
        to = NONE
        while v != -1 and made_steps < steps:
            if go_to[v] == -1:
                break
            v = go_to[v]
            made_steps += 1
        if min_dist <= made_steps <= max_dist:
            to = v
        out.write(_int_to_bytes(to))
        
dist_right = 3
dist_left = 2
for i in range(3):
    find_good_ends(dist_left, dist_right)
    dist_right += 2
    dist_left += 2

out.close()
print(time() - start_time)
