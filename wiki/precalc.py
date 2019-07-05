from GraphReader import _int_to_bytes, GraphReader
from random import shuffle

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
out = open('data/good_end_1', 'wb')

NONE = 2**32 - 1
good_end = [-1 for i in range(N)]

def find_good_ends(max_dist, min_out_edges):
    for cur_vertex in range(N):
        made_steps = 0
        out_edges = 0
        v = cur_vertex
        to = NONE
        while v != -1 and out_edges < min_out_edges and made_steps <= max_dist:
            out_edges += reader.edges_count(v)
            v = go_to[v]
            made_steps += 1
        if made_steps > 1:
            to = v
        out.write(_int_to_bytes(to))
        
max_dist = 3
min_out_edges = 400
for i in range(3):
    find_good_ends(max_dist, min_out_edges)
    max_dist += 2
    min_out_edges += 500

out.close()