import precalc_methods as precalc


class GenIteration:
    def __init__(self, graph, reversed_graph, iteration_id=0):
        self.graph = graph
        self.reversed_graph = reversed_graph
        self._paths = []
        self.start_page_id = precalc.choose_start_vertex(self.graph)
        self.title_checker = precalc.TitleChecker()
        self.dir_dist = []

    @property
    def generated_paths(self):
        return self._paths
