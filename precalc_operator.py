import argparse
from wiki.GraphReader import GraphReader
from django.conf import settings
from precalc_methods import DifficultyData
from hard_precalc import GenIterationHard
from precalc import GenIteration
import logging, sys

parser = argparse.ArgumentParser()
parser.add_argument('iter_num', help='iterations amount', type=int)
parser.add_argument('out_dir', help='output directory')
parser.add_argument('difficulty', help='difficulty', 
                    choices=['easy', 'medium', 'hard'])
parser.add_argument('--debug', help='turns debug messages on', action="store_true")
args = parser.parse_args()

l = logging.getLogger('the_logger')
if args.debug:
    l.level = logging.DEBUG
l.handlers.append(logging.StreamHandler(sys.stderr))
logging.root = l

reversed_graph = GraphReader(settings.GRAPH_OFFSET_PATH,
                             settings.GRAPH_EDGES_PATH)
graph = GraphReader(settings.REVERSE_GRAPH_OFFSET_PATH,
                    settings.REVERSE_GRAPH_EDGES_PATH)

data = DifficultyData(args.out_dir, args.difficulty)
iter_num = args.iter_num
paths = []

for iteration in range(iter_num):
    if data.difficulty == 'hard':
        currentIter = GenIterationHard(graph, reversed_graph, iteration)
    else:
        currentIter = GenIteration(graph, reversed_graph, data.difficulty, iteration)
    currentIter.run()
    paths += currentIter.generated_paths


for path in paths:
    data.add_path(path)
data.write_to_files()
