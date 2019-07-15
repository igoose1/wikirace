from random import choice
import precalc_methods as precalc
from settings_import import settings

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH
MINIMAL_OUTER_LINKS = 50
dist_range = {
    'easy': range(2, 3),
    'medium': range(3, 5)
}


class EasyBFSOperator(precalc.BFSOperator):
    def __init__(self, iteration_id):
        super().__init__(iteration_id)
        self.clear()
    
    def clear(self):
        self._go_to = [[] for i in range(VERTICES_COUNT)]    
    
    def add_edge(self, start_vertex, final_vertex):
        self._go_to[start_vertex].append(final_vertex) 


class GenIteration:
    def __init__(self, graph, reversed_graph, difficulty, iteration_id=0):
        self.graph = graph
        self.reversed_graph = reversed_graph
        self.title_checker = precalc.TitleChecker()
        self._paths = []
        self.start_page_id = precalc.choose_start_vertex(self.graph)
        self.difficulty = difficulty
        self.dist = []
        self.go_to = []
        self.bfs_operator = EasyBFSOperator(iteration_id)
        self._init_dist()

    def _init_dist(self):
        self.dist, self.go_to = precalc.bfs(self.start_page_id, self.graph, self.bfs_operator)

    def enough_outer_links(self, index):
        links_amount = self.reversed_graph.edges_count(index)
        return links_amount >= MINIMAL_OUTER_LINKS

    def is_vertex_good(self, vertex):
        return (self.enough_outer_links(vertex) and
                self.title_checker.is_title_ok(vertex) and
                self.dist[vertex] <= 5)

    def get_path_by_vertex(self, start_vertex):
        max_steps = choice(dist_range[self.difficulty])
        cur_vertex = start_vertex
        path = [start_vertex]
        while len(path) < max_steps:
            if len(self.go_to[cur_vertex]) == 0:
                return path
            next_vertex = choice(self.go_to[cur_vertex])
            path.append(next_vertex)
            cur_vertex = next_vertex
        return path

    def gen_paths(self):
        for vertex in range(VERTICES_COUNT):
            if not self.is_vertex_good(vertex):
                continue
            current_path = self.get_path_by_vertex(vertex)
            if self.is_vertex_good(current_path[-1]):
                self._paths.append(current_path)

    def run(self):
        self.gen_paths()

    @property
    def generated_paths(self):
        return self._paths
