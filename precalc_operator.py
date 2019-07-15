import argparse
from wiki.GraphReader import GraphReader
from django.conf import settings
from precalc_methods import DifficultyData
from hard_precalc_refactored import GenIterationHard
from precalc_refactored import GenIteration


parser = argparse.ArgumentParser()
parser.add_argument('iter_num', help='iterations amount', type=int)
parser.add_argument('out_dir', help='output directory')
parser.add_argument('difficulty', help='difficulty (easy/medium/hard)')
args = parser.parse_args()

reversed_graph = GraphReader(settings.GRAPH_OFFSET_PATH,
                             settings.GRAPH_EDGES_PATH)
graph = GraphReader(settings.REVERSE_GRAPH_OFFSET_PATH,
                    settings.REVERSE_GRAPH_EDGES_PATH)

data = DifficultyData(args.out_dir, args.difficulty)
iter_num = args.iter_num
paths = []

for i in range(iter_num):
    if data.difficulty == 'hard':
        currentIter = GenIterationHard(graph, reversed_graph)
    else:
        currentIter = GenIteration(graph, reversed_graph)
    currentIter.run()
    paths += currentIter.paths()


for path in paths:
    data.add_path(path)
data.write_to_files()
