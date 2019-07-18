from wiki.ZIMFile import ZIMFile, Article
from wiki.PathReader import get_path
from random import randrange
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponseServerError, Http404
from struct import unpack
from enum import Enum
from .models import Game, Turn, GamePair, MultiplayerPair, TurnType
from wiki.GraphReader import *


class GameTypes(Enum):
    random = "random"
    easy = "easy"
    medium = "medium"
    hard = "hard"
    trial = "trial"
    by_id = "by_id"


class GameTaskGenerator(object):

    def choose_game_pair(self) -> GamePair:
        raise NotImplementedError("This is super class, implement this field in child class.")

    def choose_multiplayer(self):
        return MultiplayerPair.objects.create(game_pair=self.choose_game_pair())


class RandomGameTaskGenerator(GameTaskGenerator):

    def __init__(self, zim_file: ZIMFile, graph_reader: GraphReader, max_trying_count=10):
        self._zim_file = zim_file
        self._graph_reader = graph_reader
        self.max_trying_count = max_trying_count

    def choose_game_pair(self) -> GamePair:
        start_page_id = self._zim_file.random_article().index
        end_page_id = start_page_id
        path = [start_page_id]
        for step in range(5):
            edges = list(self._graph_reader.edges(end_page_id))
            if len(edges) == 0:
                return path
            next_id = randrange(0, len(edges))
            if edges[next_id] == start_page_id:
                continue
            end_page_id = edges[next_id]
            path.append(end_page_id)

        return GamePair.get_or_create_by_path(path)

    def choose_game_pair(self) -> GamePair:
        for i in range(self.max_trying_count):
            start_page_id = self._zim_file.random_article().index
            end_page_id = start_page_id
            path = [start_page_id]
            for step in range(5):
                edges = list(self._graph_reader.edges(end_page_id))
                if len(edges) == 0:
                    break
                next_id = randrange(0, len(edges))
                if edges[next_id] == start_page_id:
                    continue
                end_page_id = edges[next_id]
                path.append(end_page_id)
            start_article = self._zim_file[start_page_id].follow_redirect()
            end_article = self._zim_file[end_page_id].follow_redirect()
            if start_article.is_redirecting or end_article.is_redirecting:  # articles are cycle redirecting
                continue
            return GamePair.get_or_create_by_path(path)
        raise HttpResponseServerError("All articles are cycle redirecting.")


class TrialGameTaskGenerator(GameTaskGenerator):

    def choose_game_pair(self) -> GamePair:
        return self._trial.game_pair

    def __init__(self, trial):
        self._trial = trial


class DifficultGameTaskGenerator(GameTaskGenerator):

    def __init__(self, difficult):
        self._difficulty = difficult

    def choose_game_pair(self) -> GamePair:
        # to use old version remove '_V2'
        file_names = settings.LEVEL_FILE_NAMES_V2
        with open(
                file_names[self._difficulty.value],
                'rb'
        ) as file:
            cnt = unpack('>I', file.read(EDGE_BLOCK_SIZE))[0]
            pair_id = randrange(0, cnt)
            path = get_path(pair_id, self._difficulty.value)

        return GamePair.get_or_create_by_path(path)


class ByIdGameTaskGenerator(GameTaskGenerator):

    def __init__(self, pair_id):
        self.pair_id = pair_id

    def choose_game_pair(self) -> GamePair:
        if not isinstance(self.pair_id, int) or self.pair_id >= 2 ** 63 or self.pair_id < 0:
            raise Http404()
        return get_object_or_404(GamePair, pair_id=self.pair_id)


class MultipayerGameTaskGenerator(GameTaskGenerator):

    def __init__(self, multiplayer):
        self._multiplayer = multiplayer

    def choose_game_pair(self):
        return self._multiplayer.game_pair

    def choose_multiplayer(self):
        return self._multiplayer


class GameOperator:
    def __init__(self, game: Game, history: list, graph_reader: GraphReader, zim_file: ZIMFile, load_testing=False):
        self._zim = zim_file
        self._reader = graph_reader
        self._history = history
        self._load_testing = load_testing
        self._game = game

    @property
    def game(self):
        return self._game

    def make_move(self, from_page, to_page, turn_type):
        Turn.objects.create(
            from_page_id=from_page,
            to_page_id=to_page,
            game_id=self._game.game_id,
            time=timezone.now(),
            turn_type=turn_type,
            step=self._game.steps + 1
        )

    def jump_back(self):
        if len(self._history) < 2:
            return
        self._history.pop()  # pop current page
        self.make_move(self._game.current_page_id, self._history[-1], TurnType.BWD)
        self._game.current_page_id = self._history[-1]

    @property
    def start_page_id(self):
        return self.game_pair.start_page_id

    @property
    def end_page_id(self):
        return self.game_pair.end_page_id

    @property
    def game_pair(self):
        return self._game.multiplayer.game_pair

    @property
    def game_id(self):
        return self._game.game_id

    @property
    def current_page(self):
        return self._zim[self.game.current_page_id]

    @property
    def first_page(self):
        return self._zim[self.start_page_id]

    @property
    def last_page(self):
        return self._zim[self.end_page_id]

    @property
    def finished(self):
        return self._game.current_page_id == self.end_page_id or self._game.surrendered

    def surrender(self):
        self._game.surrendered = True

    @property
    def surrendered(self):
        return self._game.surrendered

    @property
    def is_history_empty(self) -> bool:
        return len(self._history) <= 1

    def update_history(self, article_id: Article):
        history_index = self._history[::-1].index(article_id)
        self._history = self._history[:len(self._history) - history_index - 1]

    @property
    def path(self):
        return list(map(int, self.game.possible_path.split()))

    def is_jump_allowed(self, article: Article):
        if article.is_empty or article.is_redirecting or article.namespace != "A":
            return False
        valid_edges = list(self._reader.edges(self._game.current_page_id))
        if article.index in valid_edges or self._load_testing or article.index == self.game.current_page_id:
            return True
        elif article.index in self._history:
            self.update_history(article.index)
            return True
        else:
            return False

    def jump_to(self, article: Article):
        if article.index == self.game.current_page_id:
            return
        self.make_move(self._game.current_page_id, article.index, TurnType.FWD)
        self._game.current_page_id = article.index
        self._history.append(article.index)

    @classmethod
    def create_game(cls, game_task_generator: GameTaskGenerator, zim_file: ZIMFile, graph_reader: GraphReader):
        multiplayer = game_task_generator.choose_multiplayer()
        game = Game.objects.create(
            current_page_id=multiplayer.game_pair.start_page_id,
            start_time=timezone.now(),
            last_action_time=timezone.now(),
            multiplayer=multiplayer,
        )
        return GameOperator(game, [multiplayer.game_pair.start_page_id], graph_reader, zim_file)

    def serialize_game_operator(self) -> dict:
        self._game.save()
        return {
            "history": self._history,
            "game_id": self.game_id
        }

    @staticmethod
    def deserialize_game_operator(data=None, zim_file=None, graph_reader=None, load_testing=False):
        if not data:
            return None
        # this ugly if for backward compatibility
        if not isinstance(data, list) and not isinstance(data, dict):
            return None
        if isinstance(data, list):
            if len(data) not in [6, 7]:
                return None
            current_page_id = data[0]
            end_page_id = data[1]
            start_page_id = data[3]
            steps = data[4]
            history = data[5]
            if len(data) <= 6:
                game_pair = GamePair.get_or_create(
                    start_page_id=start_page_id,
                    end_page_id=end_page_id,
                )
                multiplayer = MultiplayerPair.objects.create(game_pair=game_pair)
                game = Game.objects.create(
                    multiplayer=multiplayer,
                    steps=steps,
                    start_time=None,
                    current_page_id=current_page_id,
                    last_action_time=timezone.now()
                )
            else:
                game = Game.objects.get(game_id=data[6])
                game.current_page_id = current_page_id
        elif "game_id" in data.keys() and 'history' in data.keys():
            game = Game.objects.get(game_id=data["game_id"])
            history = data['history']
        else:
            return None
        return GameOperator(game, history, graph_reader, zim_file, load_testing)
