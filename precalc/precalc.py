from random import choice
import precalc_methods as precalc
from settings_import import settings
from new_precalc import GenIteration

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH
MINIMAL_OUTER_LINKS = {'easy': 100, 'medium': 50}
MAXIMAL_IN_LINKS = {'easy': 100, 'medium': 1500}
dist_range = {
    'easy': range(2, 3),
    'medium': range(3, 5)
}


class EasyBFSOperator(precalc.BFSOperator):
    def __init__(self, iteration_id):
        super().__init__(iteration_id)
        self._children = [[] for _ in range(VERTICES_COUNT)]

    def add_edge(self, start_vertex, final_vertex):
        self._children[start_vertex].append(final_vertex)

    @property
    def children(self):
        return self._children


class GenIterationEasy(GenIteration):
    def __init__(self, graph, reversed_graph, difficulty, iteration_id=0):
        super().__init__(graph, reversed_graph, iteration_id)
        self.difficulty = difficulty
        self.children = []
        self.bfs_operator = EasyBFSOperator(iteration_id)
        self._init_dist()

    def _init_dist(self):
        self.dir_dist = precalc.bfs(self.start_page_id, self.graph,
                                    self.bfs_operator)
        self.children = self.bfs_operator.children

    def enough_outer_links(self, index):
        links_amount = self.reversed_graph.edges_count(index)
        return links_amount >= MINIMAL_OUTER_LINKS[self.difficulty]

    def enough_in_links(self, index):
        links_amount = self.graph.edges_count(index)
        return links_amount <= MAXIMAL_IN_LINKS[self.difficulty]

    def is_vertex_good(self, vertex):
        return (self.enough_outer_links(vertex) and
                self.enough_in_links(vertex) and
                self.title_checker.is_title_ok(vertex) and
                self.dir_dist[vertex] is not None and
                self.dir_dist[vertex] <= 5)

    def get_path_by_vertex(self, start_vertex):
        max_steps = choice(dist_range[self.difficulty])
        cur_vertex = start_vertex
        path = [start_vertex]
        while len(path) - 1 < max_steps:
            if len(self.children[cur_vertex]) == 0:
                if len(path) - 1 in dist_range[self.difficulty]:
                    return path
                return None
            next_vertex = choice(self.children[cur_vertex])
            path.append(next_vertex)
            cur_vertex = next_vertex
        return path

    def run(self):
        for vertex in range(VERTICES_COUNT):
            if not self.is_vertex_good(vertex):
                continue
            current_path = self.get_path_by_vertex(vertex)
            if current_path is not None and self.is_vertex_good(current_path[-1]):
                self._paths.append(current_path)
