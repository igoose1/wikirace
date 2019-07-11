from django.test import TestCase
import wiki.ZIMFile
from django.conf import settings
from unittest.mock import Mock
import wiki.GameOperator as Operator


class TestZIMFile(TestCase):
    def setUp(self):
        self.zim = wiki.ZIMFile.ZIMFile(settings.WIKI_ZIMFILE_PATH,
                                        settings.WIKI_ARTICLES_INDEX_FILE_PATH)

    def tearDown(self):
        self.zim.close()

    def testSmoke(self):
        article_Moscow = self.zim[2029658]
        self.assertEqual(article_Moscow.title, 'Москва')
        article_Moscow = self.zim['Москва.html']
        self.assertEqual(article_Moscow.title, 'Москва')

    def testArticleWithNamespace(self):
        article_Moscow = self.zim['A/Москва.html']
        self.assertEqual(article_Moscow.title, 'Москва')

    def testRedirect(self):
        article_redirecting = self.zim[47]
        self.assertEqual(article_redirecting.title, '!!')
        article_followed = article_redirecting.follow_redirect()
        self.assertFalse(article_followed.is_redirecting)
        self.assertFalse(article_followed.is_empty)
        self.assertEqual(article_followed.title, 'Факториал')

    def testRandomArticle(self):
        wiki.ZIMFile.randrange = Mock(return_value=1539)
        article_random = self.zim.random_article()
        self.assertEqual(article_random.title, '(566) Стереоскопия')
        self.assertEqual(article_random.index, 1946)
        self.assertFalse(article_random.is_redirecting)
        self.assertFalse(article_random.is_empty)

    def testEmptyArticle(self):
        article = self.zim['A/smth smth']
        self.assertTrue(article.is_empty)
        article_followed = article.follow_redirect()
        self.assertTrue(article_followed.is_empty)

    def testEmptyFields(self):
        article = self.zim['A/smth smth']
        smth = article.index
        smth = article.is_redirecting
        smth = article.is_empty
        smth = article.namespace
        smth = article.mimetype
        smth = article.url
        smth = article.title
        with self.assertRaises(Exception):
            smth = article.content

    def testImage(self):
        article = self.zim[3407948]
        self.assertFalse(article.is_redirecting)
        self.assertFalse(article.is_empty)
        self.assertEqual(article.namespace, 'I')
        self.assertEqual(article.index, 3407948)
        self.assertEqual(article.url, 'favicon.png')


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
