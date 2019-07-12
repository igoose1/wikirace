from wiki.GraphReader import GraphReader
from random import randrange, shuffle
from time import time

from zimply.zimply import ZIMFile

from precalc_methods import write_to_files, choose_start_vertex, only_digits, includes_bad_words
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikirace.settings")

def bfs(start_page_id, reader, walk=-1):
    dist = [-1 for i in range(N)]
    dist_cnt = dict()
    go_to = [[] for i in range(N)]
    queue = [start_page_id]
    idx = 0
    dist[start_page_id] = 0
    dist_cnt[0] = 1
    while idx < len(queue):
        cur_vertex = queue[idx]
        if dist[queue[idx]] > dist[queue[idx - 1]]:
            print('walk', walk, 'dist', dist[queue[idx]], flush=True)
            dist_cnt[dist[cur_vertex]] = 0
            if dist[cur_vertex] == 10:
                break
        dist_cnt[dist[cur_vertex]] += 1
        idx += 1
        edges = list(reader.edges(cur_vertex))
        shuffle(edges)
        for next_ in edges:
            if dist[next_] == -1:
                dist[next_] = dist[cur_vertex] + 1
                queue.append(next_)
                go_to[cur_vertex].append(next_)
    print(dist_cnt)
    return dist, go_to


start_time = time()
N = 5054753
reverse_reader = GraphReader(settings.REVERSE_GRAPH_EDGES_PATH, settings.REVERSE_GRAPH_OFFSET_PATH)
reader = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
zim = ZIMFile(settings.WIKI_ZIMFILE_PATH, 'utf-8')
easy_pairs = []
medium_pairs = []
easy_paths = []
medium_paths = []

N = 5054753
for walk in range(1):
    start_vertex = choose_start_vertex(reader)
    dist, go_to = bfs(start_vertex, reader, walk=walk)
    dists = [[2, 3], [4, 5]]
    for cur_vertex in range(N):
        v = cur_vertex
        if v % 10000 == 0:
            print('walk', walk, v, 'ready')
        if dist[v] > 5:
            continue
        cur_name = zim.read_directory_entry_by_index(cur_vertex)['title']
        if only_digits(cur_name):
            continue
        visited = []
        max_steps = randrange(dists[1][0], dists[1][1])
        while len(visited) < max_steps:
            if len(go_to[v]) == 0:
                break
            next_ = go_to[v][randrange(0, len(go_to[v]))]
            visited.append(next_)
            v = next_
        easy_steps = min(randrange(dists[0][0], dists[0][1] + 1), len(visited))
        medium_steps = min(randrange(dists[1][0], dists[1][1] + 1), len(visited))
        if easy_steps >= dists[0][0]:
            cnt1 = reverse_reader.edges_count(cur_vertex)
            cnt2 = reverse_reader.edges_count(visited[easy_steps - 1])
            if cnt1 >= 10 and cnt2 >= 10:
                name = zim.read_directory_entry_by_index(visited[easy_steps - 1])['title']
                if not only_digits(name)and not includes_bad_words(name):
                    easy_pairs.append((cur_vertex, visited[easy_steps - 1]))
                    easy_paths.append(visited[:easy_steps - 1])
        if medium_steps >= dists[1][0]:
            name = zim.read_directory_entry_by_index(visited[medium_steps - 1])['title']
            if not only_digits(name) and not includes_bad_words(name):
                medium_pairs.append((cur_vertex, visited[medium_steps - 1]))
                medium_paths.append(visited[:medium_steps - 1])

write_to_files('data/medium', 'data/medium_paths', medium_pairs, medium_paths)
write_to_files('data/easy', 'data/easy_paths', easy_pairs, easy_paths)

print(time() - start_time)
print(max(dist))
