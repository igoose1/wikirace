from django.core.management.base import BaseCommand

from wiki.ZIMFile import ZIMFile
from django.conf import settings

file = ZIMFile(
    settings.WIKI_ZIMFILE_PATH,
    settings.WIKI_ARTICLES_INDEX_FILE_PATH
)


def display_article_info(article):
    title = article.title
    url = article.url
    index = article.index
    redirecting = article.is_redirecting
    print('TITLE:       ', title, sep='')
    print('URL  :       ', url, sep='')
    print('INDEX  :       ', index, sep='')
    print('REDIRECTING: ', redirecting, sep='')


def show_redirected_info(article):
    if not article.is_redirecting:
        return

    print('[REDIRECTING]=============')
    article = article.follow_redirect()
    display_article_info(article)


def run_id():
    try:
        while True:
            print("Enter article [id]:")
            string = input()
            try:
                idx = int(string)
                article = file[idx]
                display_article_info(article)
                show_redirected_info(article)
            except:
                pass
    except:
        pass


def run_href():
    try:
        while True:
            print("Enter article [href]:")
            string = input()
            try:
                idx = string
                article = file[idx]
                display_article_info(article)
                show_redirected_info(article)
            except:
                pass
    except:
        pass


def run():
    try:
        while True:
            print("Enter ['href'] or ['idx']")
            string = input()
            try:
                if (string == 'href'):
                    run_href()
                if (string == 'idx'):
                    run_id()
            except:
                pass
    except:
        pass


class Command(BaseCommand):
    def handle(self, **options):
        run()
