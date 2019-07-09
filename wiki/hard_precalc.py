import sys
from GraphReader import GraphReader
from random import shuffle, randrange
from time import time
from zimply.zimply import ZIMFile
import struct
from precalc_methods import write_to_files, choose_start_vert, only_digits

def bfs(start_page_id, reader, walk=-1):
    dist = [-1 for i in range(N)]
    dist_cnt = dict()
    go_to = [-1 for i in range(N)]
    queue = [start_page_id]
    idx = 0
    dist[start_page_id] = 0
    dist_cnt[0] = 1
    while idx < len(queue):
        cur_vertex = queue[idx]
        if dist[queue[idx]] > dist[queue[idx - 1]]:
            print('walk', walk, 'dist', dist[queue[idx]], flush=True)
            dist_cnt[dist[cur_vertex]] = 0
            if dist[cur_vertex] == 10:
                break
        dist_cnt[dist[cur_vertex]] += 1
        idx += 1
        edges = reader.edges(cur_vertex)
        for next_ in edges:
            if dist[next_] == -1:
                dist[next_] = dist[cur_vertex] + 1
                queue.append(next_)
                go_to[next_] = cur_vertex
    print(dist_cnt)
    return dist, go_to

N = 5054753
pairs = []
paths = []
for walk in range(7):
    reader = GraphReader('data/reverse_offset', 'data/reverse_edges')
    start_page_id = choose_start_vert(reader)
    print(start_page_id)    
    rev_dist, rev_go_to = bfs(start_page_id, reader, walk=walk)
    reader = GraphReader('data/offset', 'data/edges')
    dir_dist, dir_go_to = bfs(start_page_id, reader, walk=walk)
    ok_two = []
    seven = []
    for v in range(N):
        if dir_dist[v] != -1 and dir_dist[v] < 10 and rev_dist[v] <= 2:
            ok_two.append(v)
        if rev_dist[v] == 7:
            seven.append(v)
    for fr in seven:
        to = ok_two[randrage(0, len(ok_two))]
        path = []
        v = rev_go_to[fr]
        ready = False
        while v != -1:
            path.append(v)
            v = rev_go_to[v]
            if v == to:
                path.pop()
                ready = True
                break
        if ready:
            pairs.append([fr, to])
            paths.append(path)
            continue
        sec_part = []
        v = dir_go_to[to]
        while v != -1:
            sec_part.append(v)
            v = dir_go_to[v]
        sec_part.pop()
        path += sec_part[::-1]
        pairs.append([fr, to])
        paths.append(sec_part)

write_to_files('data/hard', 'data/hard_paths', pairs, paths)