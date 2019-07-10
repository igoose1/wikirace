from wiki.ZIMFile import ZIMFile
from random import randrange
from django.conf import settings

import datetime
from struct import unpack

from .models import GameStat, Turn
from wiki.GraphReader import *

DIFFICULT_EASY = "easy"
DIFFICULT_MEDIUM = "medium"
DIFFICULT_HARD = "hard"

RANDOM_GAME_TYPE = "random"
DIFFICULT_GAME_TYPE = "difficult"


class GameTaskGenerator(object):

    def choose_start_and_end_pages(self) -> (int, int):
        pass


class RandomGameTaskGenerator(GameTaskGenerator):

    def choose_start_and_end_pages(self) -> (int, int):
        start_page_id = self._zim_file.random_article()
        end_page_id = start_page_id
        for step in range(5):
            edges = list(self._graph_reader.edges(end_page_id))
            next_id = randrange(0, len(edges))
            if edges[next_id] == start_page_id:
                continue
            end_page_id = edges[next_id]

        return start_page_id, end_page_id

    def __init__(self, zim_file: ZIMFile, graph_reader: GraphReader):
        self._zim_file = zim_file
        self._graph_reader = graph_reader


class DifficultGameTaskGenerator(GameTaskGenerator):

    def __init__(self, difficult):
        self._difficulty = difficult

    def choose_start_and_end_pages(self) -> (int, int):
        file_names = settings.LEVEL_FILE_NAMES
        file = open(file_names[self._difficulty], 'rb')
        cnt = unpack('>I', file.read(EDGE_BLOCK_SIZE))[0]
        pair_id = randrange(0, cnt - 1)
        file.seek(EDGE_BLOCK_SIZE + pair_id * EDGE_BLOCK_SIZE * 2)
        start_page_id = unpack('>I', file.read(EDGE_BLOCK_SIZE))[0]
        end_page_id = unpack('>I', file.read(EDGE_BLOCK_SIZE))[0]
        file.close()

        return start_page_id, end_page_id


class GameOperator:
    def __init__(self, game: GameStat, history: list, graph_reader: GraphReader, zim_file: ZIMFile, load_testing=False):
        self._zim = zim_file
        self._reader = graph_reader
        self._history = history
        self._load_testing = load_testing
        self._game = game

    @property
    def game(self):
        return self._game

    def navigate_previous_page(self):
        if len(self._history) >= 2:
            self._history.pop()  # pop current page
            self.game.steps += 1
            self._game.current_page_id = self._history[-1]  # pop prev page (will be added in next_page)

    @property
    def finished(self):
        return self._game.current_page_id == self._game.end_page_id

    @property
    def is_history_empty(self) -> bool:
        return len(self._history) <= 1

    # return True if next page correct
    def try_navigate_next_page(self, url: str) -> bool:

        article = self._zim[url]

        if article.is_empty:
            return False

        article = article.follow_redirect()

        if article.is_redirecting or article.namespace != "A":
            return False

        if article.index == self._game.current_page_id:
            return True

        valid_edges = list(self._reader.edges(self._game.current_page_id))

        if article.index not in valid_edges and not self._load_testing:
            return False

        self._game.steps += 1
        Turn.objects.create(
            from_page_id=self._game.current_page_id,
            to_page_id=article.index,
            game_id=self._game.game_id,
            time=datetime.datetime.now(),
        )
        self._game.current_page_id = article.index

        self._history.append(article.index)
        return True

    @classmethod
    def create_game(cls, game_task_generator: GameTaskGenerator, zim_file: ZIMFile, graph_reader: GraphReader):
        start_page_id, end_page_id = game_task_generator.choose_start_and_end_pages()
        game = GameStat.objects.create(
            start_page_id=start_page_id,
            end_page_id=end_page_id,
            current_page_id=start_page_id,
            start_time=datetime.datetime.now(),
            last_action_time=datetime.datetime.now()
        )
        return GameOperator(game, [start_page_id], graph_reader, zim_file)

    def serialize_game_operator(self) -> dict:
        self._game.finished = self.finished
        self._game.save()
        return {
            "history": self._history,
            "game_id": self._game.game_id
        }

    @staticmethod
    def deserialize_game_operator(data: dict, zim_file: ZIMFile, graph_reader: GraphReader, load_testing=False):
        if data is None:
            return None
        # this ugly if for backward compatibility
        if len(data) > 2:
            current_page_id = data[0]
            end_page_id = data[1]
            game_finished = data[2]
            start_page_id = data[3]
            steps = data[4]
            history = data[5]
            if len(data) <= 6:
                game = GameStat.objects.create(
                    start_page_id=start_page_id,
                    end_page_id=end_page_id,
                    steps=steps,
                    start_time=None,
                    current_page_id=current_page_id,
                    finished=game_finished,
                    last_action_time=datetime.datetime.now()
                )
            else:
                game = GameStat.objects.get(
                    game_id=data[6]
                )
                game.current_page_id = current_page_id
        else:
            game = GameStat.objects.get(game_id=data["game_id"])
            history = data['history']
        return GameOperator(game, history, graph_reader, zim_file, load_testing)
