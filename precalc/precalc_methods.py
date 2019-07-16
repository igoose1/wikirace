from random import randrange, shuffle
import struct
from settings_import import settings
from wiki.ZIMFile import ZIMFile
import logging
import os
import collections

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH


class DifficultyData:
    def __init__(self, out_directory, difficulty):
        self._paths = []
        self.out_directory = out_directory
        self.difficulty = difficulty
    
    def add_path(self, path):
        if path is None:
            return
        self._paths.append(path)
    
    def write_to_files(self):
        file_name = os.path.join(self.out_directory, self.difficulty)
        with open(file_name, 'wb') as pair_file, open(file_name + '_paths', 'wb') as path_file:
            number_of_pairs = len(self._paths)
            pair_file.write(struct.pack('>i', number_of_pairs))
            offset = 0
            for i in range(number_of_pairs):
                start_vertex = self._paths[i][0]
                final_vertex = self._paths[i][-1]
                pair_file.write(struct.pack('>i', start_vertex))
                pair_file.write(struct.pack('>i', final_vertex))
                pair_file.write(struct.pack('>i', offset))
                middle = self._paths[i][1:-1]
                path_file.write(struct.pack('>i', len(middle)))
                offset += 4
                for v in middle:
                    path_file.write(struct.pack('>i', v))
                    offset += 4
        
        
class BFSOperator:
    def __init__(self, iteration_id):
        self.iteration_id = iteration_id
        logging.basicConfig(level=logging.INFO)
    
    def add_edge(self, start_vertex, final_vertex):
        raise NotImplementedError("This is super class, implement add_edge() in child class.")
    
    def log(self, msg: str):
        logging.info('iteration {}: '.format(self.iteration_id) + msg)  
    
    def bad_root(self, dist_ready, dist_cnt):
        return False


MAX_BFS_DEPTH = 9


def bfs(start_page_id, reader, bfs_operator: BFSOperator):
    dist = [None] * VERTICES_COUNT
    dist_cnt = dict()
    queue = collections.deque()
    queue.append(start_page_id)
    dist[start_page_id] = 0
    dist_cnt[0] = 1
    prev_dist = 0
    while len(queue) > 0:
        cur_vertex = queue.popleft()
        if dist[cur_vertex] > prev_dist:
            dist_ready = dist[cur_vertex] - 1
            bfs_operator.log('dist {} calculated'.format(dist_ready))
            dist_cnt[dist[cur_vertex]] = 0
            if dist[cur_vertex] > MAX_BFS_DEPTH:
                break
            if bfs_operator.bad_root(dist_ready, dist_cnt[dist_ready]):
                bfs_operator.log('bad root vertex')
                return None
        prev_dist = dist[cur_vertex]
        dist_cnt[dist[cur_vertex]] += 1
        edges = list(reader.edges(cur_vertex))
        shuffle(edges)
        for next_vertex in edges:
            if dist[next_vertex] is not None:
                continue
            dist[next_vertex] = dist[cur_vertex] + 1
            queue.append(next_vertex)
            bfs_operator.add_edge(cur_vertex, next_vertex)
    bfs_operator.log('dist calculation executed')
    return dist


MIN_LINKS_FROM_ROOT = 5


def choose_start_vertex(reader):
    page_id = randrange(0, VERTICES_COUNT)
    while reader.edges_count(page_id) < MIN_LINKS_FROM_ROOT:
        page_id = randrange(0, VERTICES_COUNT)
    return page_id


class TitleChecker:
    def __init__(self):
        with open(settings.FORBIDDEN_WORDS_FILE, 'r') as f:
            self._bad_words = f.read().split()
        self.zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH,
                                settings.WIKI_ARTICLES_INDEX_FILE_PATH)

    def is_number(self, name):
        return all(c.isdigit() for c in name)
    
    def includes_bad_words(self, name):
        return any(word in name for word in self._bad_words)
    
    def is_title_ok(self, page_id):
        name = self.zim_file[page_id].title
        return not self.is_number(name) and not self.includes_bad_words(name)

    def __exit__(self):
        self.zim_file.close()
