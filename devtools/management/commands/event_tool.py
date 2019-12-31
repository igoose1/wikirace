from django.core.management.base import BaseCommand

from wiki.ZIMFile import ZIMFile
from devtools.ListFilter import RegexListFilter
from django.conf import settings
from subprocess import run as Run, PIPE
import re

TOOL_PATH = "devtools/event_tool.o"


file = ZIMFile(
    settings.WIKI_ZIMFILE_PATH,
    settings.WIKI_ARTICLES_INDEX_FILE_PATH
)


class ArticleData:
    def __init__(self, data_str):
        data = data_str.split('|')
        self.idx = int(data[0])
        self.depth = int(data[1])


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


def print_article_by_idx(article_data):
    article = file[article_data.idx]
    string = "NAME:  {0}  |[INDEX:{1}]||{2}|".format(
        article.title,
        article.index,
        article_data.depth
    )
    print(string)


def run():
    print("Enter [min] [max] [start]:")
    min, max, start = map(int, input().split())
    result = Run(
        [
            TOOL_PATH,
            "/FIND",
            settings.GRAPH_OFFSET_PATH,
            settings.GRAPH_EDGES_PATH,
            str(min),
            str(max),
            str(start)
        ],
        stdout=PIPE
    )

    nice_articles_data = list(map(ArticleData, result.stdout.decode().split()))
    sorted = []

    filter = RegexListFilter(nice_articles_data)
    filter.keyin = lambda x: file[x.idx].title
    filter.found = print_article_by_idx

    try:
        while True:
            filter.pattern = get_pattern()
            try:
                resulted = filter.filter()
            except:
                pass
    except:
        pass


class Command(BaseCommand):
    def handle(self, **options):
        run()
