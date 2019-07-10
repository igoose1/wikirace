from django.test import TestCase
import wiki.ZIMFile
from django.conf import settings
from unittest.mock import Mock


class TestZIMFile(TestCase):
    def setUp(self):
        self.zim = wiki.ZIMFile.ZIMFile(settings.WIKI_ZIMFILE_PATH,
                                        settings.WIKI_ARTICLES_INDEX_FILE_PATH)

    def tierDown(self):
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
        self.assertEqual(article_followed.is_redirecting, False)
        self.assertEqual(article_followed.is_empty, False)
        self.assertEqual(article_followed.title, 'Факториал')

    def testRandomArticle(self):
        wiki.ZIMFile.randrange = Mock(return_value=1539)
        article_random = self.zim.random_article()
        self.assertEqual(article_random.title, '(566) Стереоскопия')
        self.assertEqual(article_random.index, 1946)
        self.assertEqual(article_random.is_redirecting, False)
        self.assertEqual(article_random.is_empty, False)

    def testEmptyArticle(self):
        article = self.zim['A/smth smth']
        self.assertEqual(article.is_empty, True)
        article_followed = article.follow_redirect()
        self.assertEqual(article_followed.is_empty, True)

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
        self.assertEqual(article.is_redirecting, False)
        self.assertEqual(article.is_empty, False)
        self.assertEqual(article.namespace, 'I')
        self.assertEqual(article.index, 3407948)
        self.assertEqual(article.url, 'favicon.png')

    def testLen(self):
        self.assertEqual(len(self.zim), 5054753)
