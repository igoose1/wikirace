from random import randrange, shuffle
import struct
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikirace.settings")

N = settings.NUMBER_OF_VERTICES_IN_GRAPH


def bfs(start_page_id, reader, walk=-1, hard=False):
    dist = [-1] * N
    dist_cnt = dict()
    if hard:
        go_to = [-1 for i in range(N)]
    else:
        go_to = [[] for i in range(N)]
    queue = [start_page_id]
    queue_beginning = 0
    dist[start_page_id] = 0
    dist_cnt[0] = 0
    while queue_beginning < len(queue):
        cur_vertex = queue[queue_beginning]
        if dist[cur_vertex] > dist[queue[queue_beginning - 1]]:
            print('walk', walk, 'dist', dist[queue[queue_beginning]], flush=True)
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


def write_to_files(pair_file_name, path_file_name, pairs, paths):
    file = open(pair_file_name, 'wb')
    path_file = open(path_file_name, 'wb')
    file.write(struct.pack('>i', len(pairs)))
    off = 0
    for i in range(len(pairs)):
        p = pairs[i]
        file.write(struct.pack('>i', p[0]))
        file.write(struct.pack('>i', p[1]))
        file.write(struct.pack('>i', off))
        path_file.write(struct.pack('>i', len(paths[i])))
        off += 4
        for v in paths[i]:
            path_file.write(struct.pack('>i', v))
            off += 4
    file.close()
    path_file.close()


def choose_start_vertex(reader):
    page_id = randrange(0, N)
    while reader.edges_count(page_id) < 5:
        page_id = randrange(0, N)
    print('start vertex', page_id, flush=True)
    return page_id


def only_digits(name):
    for c in name:
        if ord(c) < ord('0') or ord(c) > ord('9'):
            return False
    return True


with open(settings.FORBIDDEN_WORDS_FILE, 'r') as f:
    bad_words = f.read().split()


def includes_bad_words(name):
    for word in bad_words:
        if word in name:
            return True
    return False
