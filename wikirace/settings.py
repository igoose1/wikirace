"""
Django settings for wikirace project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from wikirace import settings_local

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

SECRET_KEY = settings_local.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings_local.DEBUG

ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'wiki',
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wikirace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['wiki/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_DIRS = ['wiki/static']

WSGI_APPLICATION = 'wikirace.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = settings_local.DATABASES

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = settings_local.STATIC_URL
NUMBER_OF_VERTICES_IN_GRAPH = 5054753

# WIKI_MIRROR_HOST = 'http://10.5.200.206:9454/'

# Path to wiki data files
DATA_DIR = settings_local.DATA_DIR

WIKI_ZIMFILE_PATH = DATA_DIR + 'wikipedia_ru.zim'
GRAPH_OFFSET_PATH = DATA_DIR + 'graph/offset_all'
GRAPH_EDGES_PATH = DATA_DIR + 'graph/edges_all'
REVERSE_GRAPH_OFFSET_PATH = DATA_DIR + 'reverse_graph/reverse_offset'
REVERSE_GRAPH_EDGES_PATH = DATA_DIR + 'reverse_graph/reverse_edges'
WIKI_ARTICLES_INDEX_FILE_PATH = DATA_DIR + 'good_articles_list'
V1_DIR = 'precalc_pairs_v1/'
LEVEL_FILE_NAMES = {
    "easy": DATA_DIR + V1_DIR + "easy",
    "medium": DATA_DIR + V1_DIR + "precalc_pairs_v1/medium",
    "hard": DATA_DIR + V1_DIR + "precalc_pairs_v1/hard",
}
V2_DIR = 'precalc_pairs_v2/'
LEVEL_PATH_FILE_NAMES_V2 = {
    "easy": DATA_DIR + V2_DIR + 'easy_paths',
    "medium": DATA_DIR + V2_DIR + 'medium_paths',
    "hard": DATA_DIR + V2_DIR + 'hard_paths'
}
LEVEL_FILE_NAMES_V2 = {
    "easy": DATA_DIR + V2_DIR + 'easy',
    "medium": DATA_DIR + V2_DIR + 'medium',
    "hard": DATA_DIR + V2_DIR + 'hard'
}
LEVEL_AMOUNT_OF_BLOCKS_V2 = 3
LEVEL_AMOUNT_OF_BLOCKS = 2
FORBIDDEN_WORDS_FILE = DATA_DIR + 'forbidden_words.txt'