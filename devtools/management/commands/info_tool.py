from django.core.management.base import BaseCommand

from wiki.ZIMFile import ZIMFile
from django.conf import settings

file = ZIMFile(
    settings.WIKI_ZIMFILE_PATH,
    settings.WIKI_ARTICLES_INDEX_FILE_PATH
)


def run():
    try:
        while True:
            print("Enter article [id]:")
            string = input()
            try:
                idx = int(string)
                article = file[idx]
                title = article.title
                url = article.url
                redirecting = article.is_redirecting
                print('TITLE:       ', title, sep='')
                print('URL  :       ', url, sep='')
                print('REDIRECTING: ', redirecting, sep='')
            except:
                pass
    except:
        pass


class Command(BaseCommand):
    def handle(self, **options):
        run()
