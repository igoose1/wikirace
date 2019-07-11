import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'change_me_to_something_secret'
DEBUG = False
ALLOWED_HOSTS = []  # Add FQDN of your host
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Path to wiki data files
WIKI_ZIMFILE_PATH = '/srv/wikirace/data/wikipedia_ru.zim'
WIKI_ARTICLES_INDEX_FILE_PATH = '/srv/wikirace/data/good_articles_list'
GRAPH_DIR = '/srv/wikirace/data/'
GRAPH_OFFSET_PATH = GRAPH_DIR + 'offset_all'
GRAPH_EDGES_PATH = GRAPH_DIR + 'edges_all'
LEVEL_FILE_NAMES = {
    "easy": GRAPH_DIR + "easy",
    "medium": GRAPH_DIR + "medium",
    "hard": GRAPH_DIR + "hard",
}
DATA_DIR = GRAPH_DIR
LEVEL_PATH_FILE_NAMES = {
    "easy": DATA_DIR + 'ok1/easy_paths',
    "medium": DATA_DIR + 'ok1/medium_paths',
    "hard": DATA_DIR + 'ok1/hard_paths'
}
LEVEL_FILE_NAMES_NEW = {
    "easy": DATA_DIR + 'ok1/easy',
    "medium": DATA_DIR + 'ok1/medium',
    "hard": DATA_DIR + 'ok1/hard'
}
