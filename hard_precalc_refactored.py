import os
from wiki.GraphReader import GraphReader
from random import choice
from precalc_methods import write_to_files, choose_start_vertex, bfs
from time import time
from settings_import import settings

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH


class GenIteration:
    def __init__(self, iteration_number):
        self.graph = GraphReader(settings.REVERSE_GRAPH_OFFSET_PATH,
                                 settings.REVERSE_GRAPH_EDGES_PATH)
        self.reversed_graph = GraphReader(settings.GRAPH_OFFSET_PATH,
                                          settings.GRAPH_EDGES_PATH)
        self.paths = []
        self.start_page_id = choose_start_vertex(self.graph)
        self.rev_dist = []
        self.rev_go_to = []
        self.dir_dist = []
        self.dir_go_to = []
        self.iteration = iteration_number
        self.good_sources = []
        self.good_sinks = []
        self._init_dists()

    def _init_dists(self):
        self.dir_dist, self.dir_go_to = bfs(self.start_page_id,
                                            self.graph, walk=self.iteration, hard=True)
        self.rev_dist, self.rev_go_to = bfs(self.start_page_id,
                                            self.rev_graph, walk=self.iteration, hard=True)

    def is_good_sink(self, vertex):
        return 0 < self.dir_dist[vertex] < 5 and self.rev_dist[vertex] == 2

    def is_good_source(self, vertex):
        return self.rev_dist[vertex] == 7

    def gen_sources(self):
        for vertex in range(VERTICES_COUNT):
            if self.is_good_source(vertex):
                self.good_sources.append(vertex)

    def gen_sinks(self):
        for vertex in range(VERTICES_COUNT):
            if self.is_good_sink(vertex):
                self.good_sinks.append(vertex)

    def create_path(self, source, sink):
        path = [source]
        cur_vertex = self.rev_go_to[source]
        while cur_vertex != -1:
            path.append(cur_vertex)
            cur_vertex = self.rev_go_to[cur_vertex]
            if cur_vertex == sink:
                break
        if cur_vertex == sink:
            path.append(sink)
            self.paths.append(path)
            return
        from_root_part = []
        cur_vertex = self.dir_go_to[sink]
        while cur_vertex != -1:
            from_root_part.append(cur_vertex)
            cur_vertex = self.dir_go_to[cur_vertex]
        from_root_part.pop()
        path += list(reversed(from_root_part))
        self.paths.append(path)

    def cut_cycles(self):
        for j in range(len(self.paths)):
            path = self.paths[j]
            for i in range(len(path)):
                path_slice = path[i+1:]
                if path[i] in path_slice:
                    idx = path_slice.index(path[i])
                    path = path[:i] + path_slice[idx:]
                    break
            self.paths[j] = path

    def gen_paths(self):
        for source in self.good_sources:
            sink = choice(self.good_sinks)
            self.create_path(source, sink)

    def run(self):
        self.gen_sources()
        self.gen_sinks()
        self.gen_paths()
        self.cut_cycles()
