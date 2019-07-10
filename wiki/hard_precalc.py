#!/usr/bin/python3
import sys
from .GraphReader import GraphReader
from random import choice
from .precalc_methods import write_to_files, choose_start_vertex


def bfs(start_page_id, reader, walk=-1):
    dist = [-1] * N
    dist_cnt = dict()
    go_to = [-1] * N
    queue = [start_page_id]
    queue_beginning = 0
    dist[start_page_id] = 0
    dist_cnt[0] = 0
    while queue_beginning < len(queue):
        cur_vertex = queue[queue_beginning]
        if dist[queue[queue_beginning]] > dist[queue[queue_beginning - 1]]:
            print('walk', walk, 'dist', dist[queue[queue_beginning]], flush=True)
            dist_cnt[dist[cur_vertex]] = 0
            if dist[cur_vertex] == 10:
                break
        queue_beginning += 1
        dist_cnt[dist[cur_vertex]] += 1
        edges = reader.edges(cur_vertex)
        for next_ in edges:
            if dist[next_] == -1:
                dist[next_] = dist[cur_vertex] + 1
                queue.append(next_)
                go_to[next_] = cur_vertex
    print(dist_cnt)
    return dist, go_to


N = 5054753

try:
    walks = int(sys.argv[1])
except IndexError:
    print('Usage $./hard_precalc.py <iterations_amount>')
    exit(1)

pairs, paths = [], []

for walk in range(walks):
    reader = GraphReader('data/reverse_offset', 'data/reverse_edges')

    start_page_id = choose_start_vertex(reader)
    print(start_page_id)

    rev_dist, rev_go_to = bfs(start_page_id, reader, walk=walk)
    reader = GraphReader('data/offset', 'data/edges')
    dir_dist, dir_go_to = bfs(start_page_id, reader, walk=walk)

    dist_from_root_is_2, dist_from_root_is_7 = [], []

    for v in range(N):
        if dir_dist[v] != -1 and dir_dist[v] < 10 and rev_dist[v] == 2:
            dist_from_root_is_2.append(v)
        if rev_dist[v] == 7:
            dist_from_root_is_7.append(v)

    for from_vertex in dist_from_root_is_7:
        to_vertex = choice(dist_from_root_is_2)
        path = []
        v = rev_go_to[from_vertex]
        ready = False

        while v != -1:
            path.append(v)
            v = rev_go_to[v]
            if v == to_vertex:
                ready = True
                break

        if ready:
            pairs.append([from_vertex, to_vertex])
            paths.append(path)
            continue

        from_root_part = []
        v = dir_go_to[to_vertex]
        while v != -1:
            from_root_part.append(v)
            v = dir_go_to[v]

        from_root_part.pop()
        path += from_root_part[::-1]

        pairs.append([from_vertex, to_vertex])
        paths.append(path)

write_to_files('data/hard', 'data/hard_paths', pairs, paths)
