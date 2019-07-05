from random import randrange
from wiki.models import Game
from wiki.GraphReader import GraphReader, _bytes_to_int, _int_to_bytes
from django.conf import settings


class GameOperator:
    def __init__(self, zim_file, graph_reader: GraphReader):
        self.current_page_id = None
        self.end_page_id = None
        self.game_finished = True
        self.zim = zim_file
        self.reader = graph_reader
        self.start_page_id = None
        self.steps = 0
        self.history = []
        self.load_testing = False

    def save(self):
        return [self.current_page_id, self.end_page_id,
                self.game_finished, self.start_page_id, 
                self.steps, self.history]

    def load(self, saved):
        self.current_page_id = saved[0]
        self.end_page_id = saved[1]
        self.game_finished = saved[2]
        self.start_page_id = saved[3]
        self.steps = saved[4]
        self.history = saved[5]
    
    def prev_page(self)->bool:
        if len(self.history) >= 2:
            self.history.pop()  # pop current page
            self.current_page_id = self.history[-1]  # pop prev page (will be added in next_page)
            # if len(self.history) >= 1:
                # self.current_page_id = self.history.pop()
            return True
        return False
    
    def is_history_empty(self)->bool:
        return (len(self.history) <= 1)

    def initialize_game(self, level=0):
        file_names = settings.LEVEL_FILE_NAMES
        #file_names = ['data/easy', 'data/medium', 'data/hard']
        file = open(file_names[level], 'rb')
        cnt = _bytes_to_int(file.read(4))
        pair_id = randrange(0, cnt - 1)
        file.seek(4 + pair_id * 8)
        self.start_page_id = _bytes_to_int(file.read(4))
        print(self.start_page_id)
        self.current_page_id = self.start_page_id
        self.end_page_id = _bytes_to_int(file.read(4))
        file.close()
        self.game_finished = False

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
            valid_edges.append(self.current_page_id)
            if idx not in valid_edges and not self.load_testing:
                if idx in self.history:
                    self.steps += max(0, self.history[::-1].index(idx) - 1)
                    self.history = self.history[:len(self.history) - 1 - self.history[::-1].index(idx)]
                else:
                    return None
                
            if self.current_page_id != idx:
                self.steps += 1
                self.current_page_id = idx
                if not self.history or idx != self.history[-1]:
                    self.history.append(idx)

                
            self.current_page_id = idx
            finished = (self.current_page_id == self.end_page_id)
            self.game_finished = finished
            return finished
        else:
            return None