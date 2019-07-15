from random import randrange, shuffle
import struct
from settings_import import settings

VERTICES_COUNT = settings.NUMBER_OF_VERTICES_IN_GRAPH

class DifficultyData:
    def __init__(self, out_directory, difficulty_name):
        self._paths = []
        self.out_directory = out_directory
        self.difficulty_name = difficulty_name
    
    def add_pair(self, pair_path):
        self._paths.append(pair_path)
    
    def write_to_files():
        file_name = self.out_directory + self.difficulty_name
        pair_file = open(file_name, 'wb')
        path_file = open(file_name + '_path', 'wb')
        number_of_pairs = len(self._paths)
        pair_file.write(struct.pack('>i', number_of_pairs))
        offset = 0
        for i in range(number_of_pairs):
            start_vertex = self.pairs[i][0]
            final_vertex = self.pairs[i][1]
            pair_file.write(struct.pack('>i', start_vertex))
            pair_file.write(struct.pack('>i', final_vertex))
            pair_file.write(struct.pack('>i', offset))
            path_file.write(struct.pack('>i', len(paths[i])))
            offset += 4
            for v in paths[i]:
                path_file.write(struct.pack('>i', v))
                offset += 4
        file.close()
        path_file.close()


def bfs(start_page_id, reader, walk=-1, hard=False):
    dist = [-1] * VERTICES_COUNT
    dist_cnt = dict()
    if hard:
        go_to = [-1 for i in range(VERTICES_COUNT)]
    else:
        go_to = [[] for i in range(VERTICES_COUNT)]
    queue = [start_page_id]
    queue_beginning = 0
    dist[start_page_id] = 0
    dist_cnt[0] = 0
    while queue_beginning < len(queue):
        cur_vertex = queue[queue_beginning]
        if dist[cur_vertex] > dist[queue[queue_beginning - 1]]:
            print('walk', walk, 'dist', dist[cur_vertex], flush=True)
            dist_cnt[dist[cur_vertex]] = 0
            if dist[cur_vertex] == 10:
                break
            if hard and dist[cur_vertex] == 3 and dist_cnt[2] < 100:
                return None, None
        queue_beginning += 1
        dist_cnt[dist[cur_vertex]] += 1
        edges = list(reader.edges(cur_vertex))
        shuffle(edges)
        for next_ in edges:
            if dist[next_] != -1:
                continue
            dist[next_] = dist[cur_vertex] + 1
            queue.append(next_)
            if hard:
                go_to[next_] = cur_vertex
            else:
                go_to[cur_vertex].append(next_)
    print(dist_cnt)
    return dist, go_to


def choose_start_vertex(reader):
    page_id = randrange(0, VERTICES_COUNT)
    while reader.edges_count(page_id) < 5:
        page_id = randrange(0, VERTICES_COUNT)
    return page_id


class TitleChecker:
    def __init__(self):
        with open(settings.FORBIDDEN_WORDS_FILE, 'r') as f:
            self._bad_words = f.read().split()

    def is_number(name):
        return all(c.isdigit() for c in name)
    
    def includes_bad_words(name):
        return any(word in name for word in self._bad_words)
    
    def is_title_ok(name):
        return not is_number(name) and not includes_bad_words(name)
