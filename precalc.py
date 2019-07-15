#!/usr/bin/python3

from wiki.GraphReader import GraphReader
from random import randrange, choice
from time import time
from wiki.ZIMFile import ZIMFile
import precalc_methods as precalc
import sys, os
from settings_import import settings
import argparse, logging

parser = argparse.ArgumentParser()
parser.add_argument('iter_num', help='iterations amount', type=int)
parser.add_argument('out_dir', help='output directory')
args = parser.parse_args()

start_time = time()
VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH
MINIMAL_OUTER_LINKS = 50
reverse_reader = GraphReader(settings.REVERSE_GRAPH_EDGES_PATH, settings.REVERSE_GRAPH_OFFSET_PATH)
reader = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
zim = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)

dist_range = {
    'easy': range(2, 3),
    'medium': range(3, 5)
}
easy_data = precalc.DifficultyData(args.out_dir, 'easy')
medium_data = precalc.DifficultyData(args.out_dir, 'medium')
title_checker = precalc.TitleChecker()


def get_a_path(start_vertex, go_to, max_steps):
    v = start_vertex
    visited = [start_vertex]
    while len(visited) < max_steps:
        if len(go_to[v]) == 0:
            break
        next_vertex = choice(go_to[v])
        visited.append(next_vertex)
        v = next_vertex
    return visited


def choose_path_from_start(visited, dist_range):
    if len(visited) < dist_range.start:
        return None
    steps = choice(dist_range)
    return visited[:steps+1]


def enough_outer_links(index):
    links_amount = reverse_reader.edges_count(index)
    return links_amount >= MINIMAL_OUTER_LINKS


def ok_vertex(index):
    name = zim[index].title
    return enough_outer_links(index) and title_checker.is_title_ok(name)


for iter_id in range(args.iter_num):
    start_vertex = precalc.choose_start_vertex(reader)
    dist, go_to = precalc.bfs(start_vertex, reader)
    for cur_vertex in range(VERTICES_COUNT):
        if dist[cur_vertex] > 5:
            continue
        if not ok_vertex(cur_vertex):
            continue
        max_steps = dist_range['medium'].stop - 1
        path = get_a_path(cur_vertex, go_to, max_steps)
        easy_path = choose_path_from_start(path, dist_range['easy'])
        final_vertex = easy_path[-1]
        if ok_vertex(final_vertex):
            easy_data.add_pair(easy_path)

easy_data.write_to_files()
medium_data.write_to_files()

print('Execution time:', time() - start_time)
