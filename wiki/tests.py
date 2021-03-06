from django.test import TestCase, Client
from django.conf import settings
from unittest.mock import Mock, patch
from urllib.parse import quote
from django.http import HttpResponseServerError, HttpResponseNotFound
import wiki.ZIMFile
from . import GameOperator, models, get_wiki_page
from .file_holder import file_holder
from .models import GamePair, MultiplayerPair
from django.conf import settings

if (settings.ROOT_PATH != ""):
    ROOT_PATH = '/' + settings.ROOT_PATH.rstrip('/')
else:
    ROOT_PATH = ""


class TestZIMFile(TestCase):
    def setUp(self):
        self.zim = wiki.ZIMFile.ZIMFile(settings.WIKI_ZIMFILE_PATH,
                                        settings.WIKI_ARTICLES_INDEX_FILE_PATH)

    def tearDown(self):
        self.zim.close()

    def testSmoke(self):
        article_moscow = self.zim[self.zim['Москва.html'].index]
        self.assertEqual(article_moscow.title, 'Москва')
        article_moscow = self.zim['Москва.html']
        self.assertEqual(article_moscow.title, 'Москва')

    def testArticleWithNamespace(self):
        article_moscow = self.zim['A/Москва.html']
        self.assertEqual(article_moscow.title, 'Москва')

    def testRedirect(self):
        article_redirecting = self.zim[self.zim['!!.html'].index]
        self.assertEqual(article_redirecting.title, '!!')
        article_followed = article_redirecting.follow_redirect()
        self.assertFalse(article_followed.is_redirecting)
        self.assertFalse(article_followed.is_empty)
        self.assertEqual(article_followed.title, 'Факториал')

    def testRandomArticle(self):
        wiki.ZIMFile.randrange = Mock(return_value=1539)
        article_random = self.zim.random_article()
        self.assertEqual(article_random.namespace, "A")
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
        article_id = self.zim['I/favicon.png'].index
        article = self.zim[article_id]
        self.assertFalse(article.is_redirecting)
        self.assertFalse(article.is_empty)
        self.assertEqual(article.namespace, 'I')
        self.assertEqual(article.index, article_id)
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
        return GameOperator.GameOperator.deserialize_game_operator(
            data,
            self.zim,
            self.graph,
        )

    def setUp(self) -> None:
        self.zim = Mock()
        self.graph = Mock()
        self.fake_game = self.FakeGame(self.GAME_ID)
        self.patches = [
            patch.object(GameOperator.Game.objects, 'get', Mock(return_value=self.fake_game)),
            patch.object(GameOperator.Game.objects, 'create', Mock(return_value=self.fake_game)),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

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


class GetWikiPageTest(TestCase):

    def testSmoke(self):
        urls_case = (ROOT_PATH + '/', ROOT_PATH + '/game_start', ROOT_PATH + '/', ROOT_PATH + '/continue')
        for url in urls_case:
            resp = self.client.get(url, follow=True)
            self.assertEqual(resp.status_code, 200)

    def testSettings(self):
        resp = self.client.get(ROOT_PATH + '/', follow=True)
        self.assertEqual(resp.status_code, 200)
        session = self.client.session
        for dif in ('random', 'easy', 'medium', 'hard'):
            session['settings'] = {'difficulty': dif, 'name': 'test'}
            session.save()
            resp = self.client.get(ROOT_PATH + '/game_start', follow=True)
            self.assertEqual(resp.status_code, 200)

    def testOldSettings(self):
        resp = self.client.get(ROOT_PATH + '/', follow=True)
        self.assertEqual(resp.status_code, 200)
        session = self.client.session
        for num in range(-1, 3):
            session['settings'] = {'difficulty': num, 'name': 'test'}
            session.save()
            resp = self.client.get(ROOT_PATH + '/game_start', follow=True)
            self.assertEqual(resp.status_code, 200)

    def testImpossibleBack(self):
        for url in (ROOT_PATH + '/', ROOT_PATH + '/game_start'):
            resp = self.client.get(url, follow=True)
            self.assertEqual(resp.status_code, 200)

        resp = self.client.get(ROOT_PATH + '/continue', follow=True)
        article_url = resp.redirect_chain[-1][0]
        if not article_url.startswith('/'):
            article_url = '/' + article_url

        resp = self.client.get(ROOT_PATH + '/back')
        self.assertRedirects(resp, article_url)


class PlayingTest(TestCase):

    def setUp(self):
        self.zim = wiki.ZIMFile.ZIMFile(
            settings.WIKI_ZIMFILE_PATH,
            settings.WIKI_ARTICLES_INDEX_FILE_PATH
        )
        pages = ('Глоксин,_Беньямин_Петер.html',
                 '1765_год.html',
                 'XX_век.html',
                 '1992_год.html',
                 'XXV_летние_Олимпийские_игры.html',
                 'Куба_на_летних_Олимпийских_играх_1992.html')
        game_pair = GamePair.get_or_create_by_path(list(self.zim[page].index for page in pages))
        self.patches = [
            patch.object(
                GameOperator.DifficultGameTaskGenerator,
                'choose_game_pair',
                Mock(return_value=game_pair)
            )
        ]

        resp = self.client.post(ROOT_PATH + '/set_settings', data={'difficulty': 'easy'})
        self.assertEqual(resp.status_code, 200)

        for p in self.patches:
            p.start()

        for url in (ROOT_PATH + '/', ROOT_PATH + '/game_start', ROOT_PATH + '/'):
            resp = self.client.get(url, follow=True)
            self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.zim.close()

    def testSmoke(self):
        url_way = [
            ROOT_PATH + '/A/Глоксин,_Беньямин_Петер.html',
            ROOT_PATH + '/A/1765_год.html',
            ROOT_PATH + '/A/XX_век.html',
            ROOT_PATH + '/A/1992_год.html',
            ROOT_PATH + '/A/XXV_летние_Олимпийские_игры.html',
            ROOT_PATH + '/A/Куба_на_летних_Олимпийских_играх_1992.html'
        ]

        for url in url_way:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            if url == url_way[-1]:
                self.assertTrue('<title>WikiRace - Игра окончена</title>' in resp.content.decode())

    def testBackButtons(self):
        url_way = [
            ROOT_PATH + '/A/Глоксин,_Беньямин_Петер.html',
            ROOT_PATH + '/A/1765_год.html',
            ROOT_PATH + '/A/XX_век.html'
        ]

        tuple(map(self.client.get, url_way))
        resp = self.client.get(ROOT_PATH + '/back')
        self.assertRedirects(
            resp,
            quote(url_way[-2])
        )

    def testStartByKey(self):
        start_page_id = self.zim['Цензура_Википедии.html'].index
        end_page_id = self.zim['Москва.html'].index
        game_pair = models.GamePair.get_or_create(start_page_id=start_page_id, end_page_id=end_page_id)
        key = MultiplayerPair.objects.create(game_pair=game_pair).multiplayer_key
        resp = self.client.get(ROOT_PATH + '/join_game/' + str(key))
        self.assertRedirects(resp, quote(ROOT_PATH + '/A/Цензура_Википедии.html'))

    def test404ByKey(self):
        resp = self.client.get(ROOT_PATH + '/join_game/zzz')
        self.assertEqual(resp.status_code, 404)

    def test404ByKeyNull(self):
        resp = self.client.get(ROOT_PATH + '/start_by_id/')
        self.assertEqual(resp.status_code, 404)


class FileLeaksTest(TestCase):

    def testSmoke(self):

        @file_holder
        class Fake(object):
            def __init__(self):
                self.mock_file1 = Mock()
                self.mock_file1.close = Mock()

                self.mock_file2 = Mock()
                self.mock_file2.close = Mock()

                self._add_file(self.mock_file1)
                self._add_file(self.mock_file2)

        test_class = Fake()
        test_class.close()

        self.assertTrue(test_class.mock_file1.close.called)
        self.assertTrue(test_class.mock_file2.close.called)

    def testException(self):

        @file_holder
        class Fake(object):
            def __init__(self):
                self.mock_file1 = Mock()
                self.mock_file1.close = Mock()

                self._add_file(self.mock_file1)
                raise FileNotFoundError

        with self.assertRaises(FileNotFoundError):
            test_class = Fake()
            self.assertTrue(test_class.mock_file1.close.called)
