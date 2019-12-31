from django.core.management.base import BaseCommand

from wiki.ZIMFile import ZIMFile
from devtools.ListFilter import RegexListFilter
from django.conf import settings
import re


file = ZIMFile(
    settings.WIKI_ZIMFILE_PATH,
    settings.WIKI_ARTICLES_INDEX_FILE_PATH
)


def get_pattern():
    while (True):
        print("Enter filter:")
        string = input().strip()
        try:
            prog = re.compile(string)
            return prog
        except Exception as e:
            print("Incorrect Regex")
            print(e)


def keyin(idx):
    article = file[idx]
    if article.is_empty or article.is_redirecting:
        return ""
    else:
        return article.title


def print_article_by_idx(idx):
    article = file[idx]
    if not (article.is_empty or article.is_redirecting):
        string = "NAME:  {0}  |[INDEX:{1}]|".format(
            article.title,
            article.index
        )
        print(string)


def run():
    data = list(range(6000000))
    filter = RegexListFilter(data)
    filter.keyin = keyin
    filter.found = print_article_by_idx

    try:
        while True:
            filter.pattern = get_pattern()
            try:
                resulted = filter.filter()
            except Exception as e:
                print(e)
    except:
        pass


class Command(BaseCommand):
    def handle(self, **options):
        run()
