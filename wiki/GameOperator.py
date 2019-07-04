from random import randrange
#from wiki.models import Game
from GraphReader import GraphReader, _int_to_bytes, _bytes_to_int

class GameOperator:
    def __init__(self, vertices_file, graph_reader: GraphReader):
        self.current_page_id = None
        self.end_page_id = None
        self.game_finished = True
        self.vertices_file = open(vertices_file, 'rb')
        self.reader = graph_reader
        self.start_page_id = None
    
    def __exit__(self, *_):
        self.vertices_file.close()

    def save(self):
        return [self.current_page_id, self.end_page_id,
                self.game_finished, self.start_page_id]

    def load(self, saved):
        self.current_page_id = saved[0]
        self.end_page_id = saved[1]
        self.game_finished = saved[2]
        self.start_page_id = saved[3]

    def _get_random_article_id(self):
        good_verts_amount = _bytes_to_int(self.vertices_file.read(4))
        random_vert = randrange(1, good_verts_amount)
        self.vertices_file.seek(random_vert * 4)
        article_id = _bytes_to_int(self.vertices_file.read(4))
        return article_id

    def initialize_game(self):
        N = 5054753
        MAX_BFS_TREE_SIZE = 10**4
        MAX_BFS_TREE_DEPTH = 10
        MAX_DEGREE = 300
        dist = [-1 for i in range(N)]
        self.game_finished = False
        self.current_page_id = self._get_random_article_id()
        self.start_page_id = self.current_page_id        
        queue = [self.start_page_id]
        idx = 0
        dist[self.start_page_id] = 0
        last_layer = 0
        while idx < len(queue) and len(queue) < MAX_BFS_TREE_SIZE and dist[queue[idx]] < MAX_BFS_TREE_DEPTH:
            cur_vertex = queue[idx]
            #print(cur_vertex)
            idx += 1
            if self.reader.edges_count(cur_vertex) > MAX_DEGREE:
                continue
            edges = self.reader.Edges(cur_vertex)
            for next_ in edges:
                if dist[next_] == -1:
                    dist[next_] = dist[cur_vertex] + 1
                    queue.append(next_)
                    if dist[next_] > dist[queue[-2]]:
                        last_layer = len(queue) - 1
                    if len(queue) >= MAX_BFS_TREE_SIZE:
                        break
        self.end_page_id = queue[randrange(last_layer, len(queue) - 1)]
        print(dist[self.end_page_id])
        
    def next_page(self, relative_url: str):
        if self.game_finished:
            return True
        _, namespace, *url_parts = relative_url.split('/')

        url = None
        if (namespace == 'A'):
            url = "/".join(url_parts)
        if (len(namespace) > 1):
            url = namespace

        already_finish = (self.current_page_id == self.end_page_id);
        self.game_finished = already_finish
        if already_finish:
            return True

        if url:
            entry, idx = self.zim._get_entry_by_url("A", url)
            article = self.zim.get_by_index(idx)
            if article is None:
                return None

            while 'redirectIndex' in entry.keys():
                idx = entry['redirectIndex']
                entry = self.zim.read_directory_entry_by_index(idx)
            if entry['namespace'] != 'A':
                return None

            valid_edges = list(self.reader.Edges(self.current_page_id))

            if idx not in valid_edges:
                return False

            self.current_page_id = idx

            finished = (self.current_page_id == self.end_page_id)
            self.game_finished = finished
            return finished
        else:
            return None