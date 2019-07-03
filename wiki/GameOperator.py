from random import randrange
from wiki.GraphReader import GraphReader

class GameOperator:
    def __init__(self, zim_file, graph_reader:GraphReader):
        self.current_page_id = None
        self.end_page_id = None
        self.game_finished = True
        self.zim = zim_file
        self.reader = graph_reader
    def save(self):
        return [self.current_page_id, self.end_page_id,
                self.game_finished]
    def load(self, saved):
        self.current_page_id = saved[0]
        self.end_page_id = saved[1]
        self.game_finished = saved[2]
    def _get_random_article_id(self):
        article_id = randrange(0, len(self.zim))
        article = self.zim.get_by_index(article_id)
        while (article is None) or article.namespace != "A":
            article_id = randrange(0, len(self.zim))
            article = self.zim._get_article_by_index(article_id)
            
        entry = self.zim.read_directory_entry_by_index(article_id)
        while 'redirectIndex' in entry.keys():
            article_id = entry['redirectIndex']
            entry = self.zim.read_directory_entry_by_index(article_id)
            
        return article_id
    def initialize_game(self):
        self.game_finished = False
        self.current_page_id = self._get_random_article_id()
        while self.reader.edges_count(self.current_page_id) == 0:
            self.current_page_id = self._get_random_article_id()
            
        end_page_id_tmp = self.current_page_id
        for step in range(5):
            edges = list(self.reader.Edges(end_page_id_tmp))
            next_id = randrange(0, len(edges))
            if (edges[next_id] == self.current_page_id):
                break
            end_page_id_tmp = edges[next_id]
        self.end_page_id = end_page_id_tmp
    def next_page(self, relative_url:str):
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
            entry, idx = self.zim._get_entry_by_url("A",url)
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
        
