from django.core.management.base import BaseCommand

from wiki.ZIMFile import ZIMFile
from django.conf import settings
from subprocess import run as Run, PIPE

TOOL_PATH = "devtools/event_tool.o"


file = ZIMFile(
    settings.WIKI_ZIMFILE_PATH,
    settings.WIKI_ARTICLES_INDEX_FILE_PATH
)


def run():
    print("Enter [start] [end]:")
    start, end = map(int, input().split())
    result = Run(
        [
            TOOL_PATH,
            "/MINPATH",
            settings.GRAPH_OFFSET_PATH,
            settings.GRAPH_EDGES_PATH,
            str(start),
            str(end)
        ],
        stdout=PIPE
    )

    path = list(map(int, result.stdout.decode().split()))

    idx = 0
    print()
    print('====================')
    for article_idx in path:
        article = file[article_idx]
        title = article.title
        url = article.url
        index = article.index
        if idx > 0:
            print("[[{0}]]".format(idx))
        print(" TITLE: {0}".format(title))
        print(" INDEX: {0}".format(index))
        print(" URL  : {0}".format(url))
        idx += 1
        if idx < len(path):
            print("|\n|")


class Command(BaseCommand):
    def handle(self, **options):
        run()
