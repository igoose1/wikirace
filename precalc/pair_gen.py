import fast_calc
import argparse
import random
import settings_import
from wiki.ZIMFile import ZIMFile
from precalc_methods import DifficultyData, TitleChecker

parser = argparse.ArgumentParser()
parser.add_argument('out_dir', help='output directory', default='')
parser.add_argument('difficulty', help='difficulty',
                    choices=['easy', 'medium', 'hard'], default='hard')
parser.add_argument('max_paths', help='Max count of finish articles got with same start article', default=3)
parser.add_argument('att_count', help='Count of start articles', default=1)
parser.add_argument('thread_num', help='Postfit in the output file name to merge', default=0)
args = parser.parse_args()

diff_distances = {
    "easy": range(2, 3),
    "medium": range(4, 5),
    "hard": range(6, 9),
}

settings = settings_import.settings

dist_range = diff_distances[args.difficulty]
result = DifficultyData(args.out_dir, args.difficulty)
zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
checker = TitleChecker(zim_file)

for i in range(int(args.att_count)):
    graph_reader = fast_calc.GraphReader(settings.GRAPH_PATH)
    start_vertex = zim_file.random_article().index
    while not checker.is_title_ok(start_vertex):
        start_vertex = zim_file.random_article().index
    bfs_result = fast_calc.bfs(start_vertex, dist_range.stop, graph_reader)

    iter_result = []

    for vertex in bfs_result:
        if vertex.depth in dist_range:
            iter_result.append(vertex)
    iter_result = random.choices(iter_result, k=min(int(args.max_paths), len(iter_result)))
    for vertex in iter_result:
        result.add_path(fast_calc.get_path(vertex))

result.write_to_files(args.thread_num)
