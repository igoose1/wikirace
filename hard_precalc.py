#!/usr/bin/python3
import sys
from wiki.GraphReader import GraphReader
from random import choice, shuffle
from precalc_methods import write_to_files, choose_start_vertex
from time import time
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikirace.settings")
N = settings.NUMBER_OF_VERTICES_IN_GRAPH

try:
    walks = int(sys.argv[1])
except IndexError:
    print('Usage $./hard_precalc.py <iterations_amount>')
    exit(1)

pairs, paths = [], []
start_time = time()

for walk in range(walks):
    reader = GraphReader(settings.REVERSE_GRAPH_OFFSET_PATH, settings.REVERSE_GRAPH_EDGES_PATH)

    start_page_id = choose_start_vertex(reader)
    print(start_page_id)

    rev_dist, rev_go_to = bfs(start_page_id, reader, walk=walk, hard=True)
    if rev_dist is None:
        continue
    reader = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    dir_dist, dir_go_to = bfs(start_page_id, reader, walk=walk, hard=True)
    if dir_dist is None:
        continue

    dist_from_root_is_2, dist_from_root_is_7 = [], []

    for v in range(N):
        if dir_dist[v] != -1 and dir_dist[v] < 5 and rev_dist[v] == 2:
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
        for i in range(len(path)):
            path_slice = path[i+1:]
            if path[i] in path_slice:
                idx = path_slice.index(path[i])
                path = path[:i] + path_slice[idx:]
                break

        pairs.append([from_vertex, to_vertex])
        paths.append(path)

write_to_files(os.path.join(OUT_DIR, 'hard'),
    os.path.join(OUT_DIR, 'hard_paths'),
    easy_pairs, easy_paths)

print('program executed in', time() - start_time)
