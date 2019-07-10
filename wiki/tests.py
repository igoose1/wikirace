from django.test import TestCase
from unittest.mock import Mock
import wiki.GameOperator as Operator


class GameOperatorTest(TestCase):
    game_id = 6

    class FakeGame(object):
        def __init__(self, game_id):
            self.game_id = game_id
            self.start_page_id = 1
            self.end_page_id = 2
            self.current_page_id = 3
            self.steps = 4
            self.start_time = None
            self.last_action_time = 0

    def setUp(self) -> None:
        self.zim = Mock()
        self.graph = Mock()
        self.fake_game = self.FakeGame(self.game_id)
        Operator.Game.objects.get = Mock(return_value=self.fake_game)
        Operator.Game.objects.create = Mock(return_value=self.fake_game)

    def test_backward_compatibility_1(self):
        game_operator = Operator.GameOperator.deserialize_game_operator(
            [1, 2, True, 3, 4, [5]],
            self.zim,
            self.graph
        )
        self.assertNotEqual(game_operator, None)
        self.assertEqual(game_operator.game, self.fake_game)

    def test_backward_compatibility_2(self):
        game_operator = Operator.GameOperator.deserialize_game_operator(
            [1, 2, True, 3, 4, [5], self.game_id],
            self.zim,
            self.graph
        )
        self.assertNotEqual(game_operator, None)
        self.assertEqual(game_operator.game, self.fake_game)

    def test_deserialize_error_with_null_data(self):
        game_operator = Operator.GameOperator.deserialize_game_operator(
            None,
            self.zim,
            self.graph
        )
        self.assertEqual(game_operator, None)

    def test_deserialize_error_with_error_data(self):
        game_operator = Operator.GameOperator.deserialize_game_operator(
            [1, 2],
            self.zim,
            self.graph
        )
        self.assertEqual(game_operator, None)

        game_operator = Operator.GameOperator.deserialize_game_operator(
            {
                "test1": "smth",
                "test2": "smth",
                "game_id": self.game_id
            },
            self.zim,
            self.graph
        )
        self.assertEqual(game_operator, None)
