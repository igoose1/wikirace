#!/usr/bin/python3

from wiki.GraphReader import GraphReader
from random import randrange
from time import time
from wiki.ZIMFile import ZIMFile

from precalc_methods import write_to_files, choose_start_vertex, only_digits, includes_bad_words, bfs
from django.conf import settings
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikirace.settings")

try:
    walks = int(sys.argv[1])
except IndexError or TypeError:
    print('Usage $./precalc.py <iterations_amount> <output_directory>')
    exit(1)

try:
    OUT_DIR = sys.argv[2]
except IndexError:
    print('Usage: $./precalc.py <iterations_amount> <output_directory>')
    exit(1)

start_time = time()
N = settings.NUMBER_OF_VERTICES_IN_GRAPH
reverse_reader = GraphReader(settings.REVERSE_GRAPH_EDGES_PATH, settings.REVERSE_GRAPH_OFFSET_PATH)
reader = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
zim = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
easy_pairs = []
medium_pairs = []
easy_paths = []
medium_paths = []
dist_range = {
    'easy': [2, 2],
    'medium' : [3, 4]
}


def ok_name(name):
    return not only_digits(name) and not includes_bad_words(name)


def add_pair_if_ok(start, visited, level, pairs, paths, outer_links=50, start_name=None):
    if len(visited) < dist_range[level][0]:
        return
    steps = min(randrange(dist_range[level][0], dist_range[level][1] + 1), len(visited))
    final = visited[steps-1]
    links_to_start_page = reverse_reader.edges_count(start)
    links_to_final_page = reverse_reader.edges_count(final)
    if links_to_start_page >= outer_links and links_to_final_page >= outer_links:
        final_name = zim[final].title
        if start_name is None:
            start_name = zim[start].title
            if not ok_name(start_name):
                return
        if ok_name(final_name):
            pairs.append((start, final))
            paths.append(visited[:steps - 1])


for walk in range(walks):
    start_vertex = choose_start_vertex(reader)
    dist, go_to = bfs(start_vertex, reader, walk=walk)
    for cur_vertex in range(N):
        if cur_vertex % 10000 == 0:
            print('walk', walk, cur_vertex, 'ready')
        if dist[cur_vertex] > 5:
            continue
        cur_name = zim[cur_vertex].title
        if ok_name(cur_name):
            continue
        visited = []
        max_steps = 5
        v = cur_vertex
        while len(visited) < max_steps:
            if len(go_to[v]) == 0:
                break
            next_vertex = go_to[v][randrange(0, len(go_to[v]))]
            visited.append(next_vertex)
            v = next_vertex
        add_pair_if_ok(cur_vertex, visited, 'easy',
                       easy_pairs, easy_paths, start_name=cur_name)
        add_pair_if_ok(cur_vertex, visited, 'medium',
                       medium_pairs, medium_paths, start_name=cur_name)


write_to_files(os.path.join(OUT_DIR, 'medium'),
               os.path.join(OUT_DIR, 'medium_paths'),
               medium_pairs, medium_paths)
write_to_files(os.path.join(OUT_DIR, 'easy'),
               os.path.join(OUT_DIR, 'easy_paths'),
               easy_pairs, easy_paths)

print('Execution time:', time() - start_time)
