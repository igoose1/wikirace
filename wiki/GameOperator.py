from wiki.ZIMFile import ZIMFile
from random import randrange
from django.conf import settings
import datetime

from byte_convert import bytes_to_int
from .models import GameStat, Turn
from wiki.GraphReader import GraphReader

DIFFICULT_EASY = "easy"
DIFFICULT_MEDIUM = "medium"
DIFFICULT_HARD = "hard"

RANDOM_GAME_TYPE = "random"
DIFFICULT_GAME_TYPE = "difficult"


class GameOperator:
	def __init__(self, game: GameStat, history: list, graph_reader: GraphReader, zim_file: ZIMFile):
		self._zim = zim_file
		self._reader = graph_reader
		self._history = history
		self._load_testing = False
		self._game = game

	def prev_page(self):
		if len(self._history) >= 2:
			self._history.pop()  # pop current page
			self._game.current_page_id = self._history[-1]  # pop prev page (will be added in next_page)

	@property
	def finished(self):
		return self._game.current_page_id == self._game.end_page_id

	@property
	def is_history_empty(self) -> bool:
		return len(self._history) <= 1

	# return True if next page correct
	# return False if next page not correct
	def next_page(self, url: str) -> bool:
		article = self._zim[url]

		if article.is_empty:
			return False

		article.follow_redirect()

		if article.is_redirecting or article.namespace != "A":
			return False

		valid_edges = list(self._reader.edges(self._game.current_page_id))
		valid_edges.append(self._game.current_page_id)
		if article.index not in valid_edges and not self._load_testing:
			if article.index in self._history:
				self._game.steps += max(0, self._history[::-1].index(article.index) - 1)
				self._history = self._history[:len(self._history) - 1 - self._history[::-1].index(article.index)]
			else:
				return False

		if self._game.current_page_id != article.index:
			self._game.steps += 1
			Turn.objects.create(
				from_page_id=self._game.current_page_id,
				to_page_id=article.index,
				game_id=self._game.game_id,
				time=datetime.datetime.now(),
			)
			self._game.current_page_id = article.index

		if not self._history or article.index != self._history[-1]:
			self._history.append(article.index)
		return True

	@staticmethod
	def _create_random_game(zim_file: ZIMFile, graph_reader: GraphReader):
		start_page_id = zim_file.random_article()
		current_page_id = start_page_id
		history = [start_page_id]
		end_page_id = current_page_id

		for step in range(5):
			edges = list(graph_reader.edges(end_page_id))
			next_id = randrange(0, len(edges))
			if edges[next_id] == current_page_id:
				continue
			end_page_id = edges[next_id]

		game = GameStat.objects.create(
			start_page_id=start_page_id,
			end_page_id=end_page_id,
			current_page_id=current_page_id,
			start_time=datetime.datetime.now(),
			last_action_time=datetime.datetime.now()
		)
		return GameOperator(game, history, graph_reader, zim_file)

	@staticmethod
	def _create_game_with_difficult(zim_file: ZIMFile, graph_reader: GraphReader, difficult=DIFFICULT_EASY):
		file_names = settings.LEVEL_FILE_NAMES
		file = open(file_names[difficult], 'rb')
		cnt = bytes_to_int(file.read(4))
		pair_id = randrange(0, cnt - 1)
		file.seek(4 + pair_id * 8)
		start_page_id = bytes_to_int(file.read(4))
		current_page_id = start_page_id
		end_page_id = bytes_to_int(file.read(4))
		file.close()
		history = [start_page_id]
		game = GameStat.objects.create(
			start_page_id=start_page_id,
			end_page_id=end_page_id,
			current_page_id=current_page_id,
			start_time=datetime.datetime.now(),
			last_action_time=datetime.datetime.now()
		)
		return GameOperator(game, history, graph_reader, zim_file)

	_game_dict = {
		RANDOM_GAME_TYPE: _create_random_game,
		DIFFICULT_GAME_TYPE: _create_game_with_difficult
	}

	@classmethod
	def create_game(cls, game_type: str, *args):
		return cls._game_dict[game_type](args)

	def serialize_game_operator(self) -> dict:
		self._game.finished = self.finished
		self._game.save()
		return {
			"history": self._history,
			"game_id": self._game.game_id
		}

	@staticmethod
	def deserialize_game_operator(data: dict, zim_file: ZIMFile, graph_reader: GraphReader):
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
		return GameOperator(game, history, graph_reader, zim_file)
