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
GRAPH_DIR = '/srv/wikirace/data/'
GRAPH_OFFSET_PATH = GRAPH_DIR + 'offset_all'
GRAPH_EDGES_PATH = GRAPH_DIR + 'edges_all'
