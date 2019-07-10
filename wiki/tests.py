from django.test import TestCase
from unittest.mock import Mock
import wiki.GameOperator as Operator


class GameOperatorTest(TestCase):
    GAME_ID = 6

    class FakeGame(object):
        def __init__(self, game_id):
            self.game_id = game_id
            self.start_page_id = 1
            self.end_page_id = 2
            self.current_page_id = 3
            self.steps = 4
            self.start_time = None
            self.last_action_time = 0

    def generate_operator(self, data):
        return Operator.GameOperator.deserialize_game_operator(
            data,
            self.zim,
            self.graph,
        )

    def setUp(self) -> None:
        self.zim = Mock()
        self.graph = Mock()
        self.fake_game = self.FakeGame(self.GAME_ID)
        Operator.Game.objects.get = Mock(return_value=self.fake_game)
        Operator.Game.objects.create = Mock(return_value=self.fake_game)

    def test_backward_compatibility_v1(self):
        game_operator = self.generate_operator(
            [1, 2, True, 3, 4, [5]]
        )
        self.assertNotEqual(game_operator, None)
        self.assertEqual(game_operator.game, self.fake_game)

    def test_backward_compatibility_v2(self):
        game_operator = self.generate_operator(
            [1, 2, True, 3, 4, [5], self.GAME_ID]
        )
        self.assertNotEqual(game_operator, None)
        self.assertEqual(game_operator.game, self.fake_game)

    def test_deserialize_error_with_null_data(self):
        game_operator = self.generate_operator(None)
        self.assertEqual(game_operator, None)

    def test_deserialize_error_with_wrong_data(self):
        game_operator = self.generate_operator([1, 2])
        self.assertEqual(game_operator, None)

        game_operator = self.generate_operator(
            {
                "test1": "smth",
                "test2": "smth",
                "game_id": self.GAME_ID
            }
        )
        self.assertEqual(game_operator, None)
