from random import randrange
import datetime

from .models import GameStat, Turn
from wiki.GraphReader import GraphReader


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
        self.game = None

    def save(self):
        self.game.finished = self.game_finished
        self.game.steps = self.steps
        self.game.last_action_time = datetime.datetime.now()
        self.game.save()
        return [self.current_page_id, self.end_page_id,
                self.game_finished, self.start_page_id, 
                self.steps, self.history,
                self.game.game_id]

    def load(self, saved):
        self.current_page_id = saved[0]
        self.end_page_id = saved[1]
        self.game_finished = saved[2]
        self.start_page_id = saved[3]
        self.steps = saved[4]
        self.history = saved[5]
        if len(saved) <= 6:
            self.game = GameStat.objects.create(
                start_page_id=self.start_page_id,
                end_page_id=self.end_page_id,
                start_time=None,
                last_action_time=datetime.datetime.now()
            )
        else:
            self.game = GameStat.objects.get(
                game_id=saved[6]
            )

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
        self.steps = 0
        self.game_finished = False
        self.current_page_id = self._get_random_article_id()
        self.start_page_id = self.current_page_id
        self.history = [self.start_page_id]
        while self.reader.edges_count(self.current_page_id) == 0:
            self.current_page_id = self._get_random_article_id()

        end_page_id_tmp = self.current_page_id
        for step in range(5):
            edges = list(self.reader.Edges(end_page_id_tmp))
            next_id = randrange(0, len(edges))
            if edges[next_id] == self.current_page_id:
                break
            end_page_id_tmp = edges[next_id]
        self.end_page_id = end_page_id_tmp

        self.game = GameStat.objects.create(
            start_page_id=self.start_page_id,
            end_page_id=self.end_page_id,
            start_time=datetime.datetime.now(),
            last_action_time=datetime.datetime.now()
        )
    
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

            if idx not in valid_edges and not self.load_testing:
                if idx in self.history:
                    self.steps += max(0, self.history[::-1].index(idx) - 1)
                    self.history = self.history[:len(self.history) - 1 - self.history[::-1].index(idx)]
                else:
                    return None
                
            if self.current_page_id != idx:
                self.steps += 1
                Turn.objects.create(
                    from_page_id=self.current_page_id,
                    to_page_id=idx,
                    game_id=self.game.game_id,
                    time=datetime.datetime.now(),
                )
                self.current_page_id = idx

            if not self.history or idx != self.history[-1]:
                self.history.append(idx)

            finished = (self.current_page_id == self.end_page_id)
            self.game_finished = finished
            return finished
        else:
            return None
