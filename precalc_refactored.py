from wiki.GraphReader import GraphReader
from random import choice
from time import time
from wiki.ZIMFile import ZIMFile
import precalc_methods as precalc
from settings_import import settings
import argparse

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH
MINIMAL_OUTER_LINKS = 50
dist_range = {
    'easy': range(2, 3),
    'medium': range(3, 5)
}


class EasyBFSOperator(precalc.BFSOperator):
    def __init__(self, iteration_id):
        super().__init__(iteration_id)
        self._go_to = [-1 for i in range(VERTICES_COUNT)]
    
    def add_edge(self, start_vertex, final_vertex):
        self._go_to[final_vertex] = start_vertex 


class GenIteration:
    def __init__(self, graph, reversed_graph, zim_file):
        self.graph = graph
        self.reversed_graph = reversed_graph
        self.zim_file = zim_file
        self.title_checker = precalc.TitleChecker()
        self.paths = []
        self.start_page_id = precalc.choose_start_vertex(self.graph)
        self.dist = []
        self.go_to = []

    def enough_outer_links(self, index):
        links_amount = self.reversed_graph.edges_count(index)
        return links_amount >= MINIMAL_OUTER_LINKS

    def is_vertex_good(self, vertex):
        return (self.enough_outer_links(vertex) and
                self.title_checker.is_title_ok(vertex))







