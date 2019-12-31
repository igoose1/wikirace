import os

STATIC_URL = '/static/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'change_me_to_something_secret'
DEBUG = False
ROOT_PATCH = ""
ALLOWED_HOSTS = []  # Add FQDN of your host
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Path to wiki data files
DATA_DIR = '/srv/wikirace/data/'
