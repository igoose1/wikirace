from random import choice
import precalc_methods as precalc
from settings_import import settings
import logging

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH
DESTINATION_LEVEL = 2
SOURCE_LEVEL = 7
MIN_DESTINATION_COUNT = 100
MAX_PATH_LENGTH = 13


def cut_cycles(path):
    for i in range(len(path)):
        path_slice = path[i + 1:]
        if path[i] in path_slice:
            idx = path_slice.index(path[i])
            path = path[:i] + path_slice[idx:]
            break
    return path


class HardBFSOperator(precalc.BFSOperator):
    def __init__(self, iteration_id):
        super().__init__(iteration_id)
        self.clear()
    
    def clear(self):
        self._go_to = [-1 for i in range(VERTICES_COUNT)]
    
    def add_edge(self, start_vertex, final_vertex):
        self._go_to[final_vertex] = start_vertex
    
    def bad_root(self, dist_ready, dist_cnt):
        return dist_ready == DESTINATION_LEVEL and dist_cnt < MIN_DESTINATION_COUNT


class GenIterationHard:
    def __init__(self, graph, reversed_graph, iteration_id=0):
        self.graph = graph
        self.reversed_graph = reversed_graph
        self._paths = []
        self.start_page_id = precalc.choose_start_vertex(self.graph)
        self.title_checker = precalc.TitleChecker()
        self.rev_dist = []
        self.rev_go_to = []
        self.dir_dist = []
        self.dir_go_to = []
        self.good_sources = []
        self.good_sinks = []
        self.bfs_operator = HardBFSOperator(iteration_id)
        self._init_dists()

    def _init_dists(self):
        self.dir_dist = precalc.bfs(self.start_page_id, 
                                    self.graph, self.bfs_operator)
        self.dir_go_to = self.bfs_operator.go_to
        self.rev_dist = precalc.bfs(self.start_page_id,
                                    self.reversed_graph, self.bfs_operator)
        self.rev_go_to = self.bfs_operator.go_to

    def is_good_sink(self, vertex):
        '''
        We choose vertices which are <DESTINATION_LEVEL> steps away from
        root vertex (in reversed graph). Root vertex is named self.start_page_id
        These vertices are potential finish articles. Potential start vertices 
        are <SOURCE_LEVEL> steps away from root vertex.
        By that choice we garantee that the shortest path from source (start) to
        sink (finish) is not shorter than 5 steps. Then we find paths from
        source to root and from root to sink. We make sure this path exists
        and it is not longer than <MAX_PATH_LENGTH> in this function.
        '''        
        max_dir_dist = MAX_PATH_LENGTH - SOURCE_LEVEL
        return (self.title_checker.is_title_ok(vertex) and
                self.dir_dist[vertex] is not None and 
                self.dir_dist[vertex] <= max_dir_dist and 
                self.rev_dist[vertex] == DESTINATION_LEVEL)

    def is_good_source(self, vertex):
        return (self.title_checker.is_title_ok(vertex) and
                self.rev_dist[vertex] == SOURCE_LEVEL)

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
            return path
        from_root_part = []
        cur_vertex = sink
        while cur_vertex != -1:
            from_root_part.append(cur_vertex)
            cur_vertex = self.dir_go_to[cur_vertex]
        from_root_part.pop()
        path += list(reversed(from_root_part))
        return path

    def gen_paths(self):
        for source in self.good_sources:
            sink = choice(self.good_sinks)
            self._paths += [cut_cycles(path) for path in self.create_path(source, sink)]

    def run(self):
        self.gen_sources()
        self.gen_sinks()
        logging.info('sources and sinks generated')
        self.gen_paths()
        self.cut_cycles()
        logging.info('paths generated')
    
    @property
    def generated_paths(self):
        return self._paths
