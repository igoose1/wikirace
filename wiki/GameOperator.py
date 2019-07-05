from random import randrange
#from wiki.models import Game
from GraphReader import GraphReader, _int_to_bytes, _bytes_to_int
import time


class GameOperator:
    def __init__(self, zim_file, graph_reader: GraphReader):
        self.current_page_id = None
        self.end_page_id = None
        self.game_finished = True
        self.zim = zim_file
        self.reader = graph_reader
        self.start_page_id = None
        self.steps = 0

    def save(self):
        return [self.current_page_id, self.end_page_id,
                self.game_finished, self.start_page_id, self.steps]

    def load(self, saved):
        self.current_page_id = saved[0]
        self.end_page_id = saved[1]
        self.game_finished = saved[2]
        self.start_page_id = saved[3]
        self.steps = saved[4]
        
    def initialize_game(self, level=0):
        file_names = ['data/easy', 'data/medium', 'data/hard']
        file = open(file_names[level], 'rb')
        cnt = _bytes_to_int(file.read(4))
        pair_id = randrange(0, cnt - 1)
        file.seek(4 + pair_id * 8)
        self.start_page_id = _bytes_to_int(file.read(4))
        self.current_page_id = self.start_page_id
        self.end_page_id = _bytes_to_int(file.read(4))
        file.close()

    def next_page(self, relative_url: str)->bool:
        if self.game_finished:
            return True
        _, namespace, *url_parts = relative_url.split('/')

        url = None
        if namespace == 'A':
            url = "/".join(url_parts)
        if len(namespace) > 1:
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

            if (self.current_page_id != idx):
                self.steps += 1
                self.current_page_id = idx

            finished = (self.current_page_id == self.end_page_id)
            self.game_finished = finished
            return finished
        else:
            return None
