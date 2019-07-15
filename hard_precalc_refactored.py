from random import choice
import precalc_methods as precalc
from settings_import import settings

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH
DESTINATION_LEVEL = 2
SOURCE_LEVEL = 7
MIN_DESTINATION_COUNT = 100
MAX_PATH_LENGTH = 13

class HardBFSOperator(precalc.BFSOperator):
    def __init__(self, iteration_id):
        super().__init__(iteration_id)
        self._go_to = [-1 for i in range(VERTICES_COUNT)]
    
    def add_edge(self, start_vertex, final_vertex):
        self._go_to[final_vertex] = start_vertex
    
    def bad_root(self, dist_ready, dist_cnt):
        return dist_ready == DESTINATION_LEVEL and dist_cnt < MIN_DESTINATION_COUNT


class GenIterationHard:
    def __init__(self, graph, reversed_graph):
        self.graph = graph
        self.reversed_graph = reversed_graph
        self.paths = []
        self.start_page_id = precalc.choose_start_vertex(self.graph)
        self.title_checker = precalc.TitleChecker()
        self.rev_dist = []
        self.rev_go_to = []
        self.dir_dist = []
        self.dir_go_to = []
        self.good_sources = []
        self.good_sinks = []
        self._init_dists()

    def _init_dists(self):
        self.dir_dist, self.dir_go_to = precalc.bfs(self.start_page_id,
                                                    self.graph, hard=True)
        self.rev_dist, self.rev_go_to = precalc.bfs(self.start_page_id,
                                                    self.rev_graph, hard=True)

    def is_good_sink(self, vertex):
        max_dir_dist = MAX_PATH_LENGTH - SOURCE_LEVEL
        return (self.dir_dist[vertex] is not None and 
                self.dir_dist[vertex] <= max_dir_dist and 
                self.rev_dist[vertex] == DESTINATION_LEVEL)

    def is_good_source(self, vertex):
        return self.rev_dist[vertex] == SOURCE_LEVEL

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

    def paths(self):
        return self.paths
