from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from . import get_wiki_page


urlpatterns = [
    path('admin', admin.site.urls),
    url('^$', get_wiki_page.get_main_page),
    url('game_start', get_wiki_page.get_start),
    url('continue', get_wiki_page.get_continue),
    url('back', get_wiki_page.get_back),
    url('hint_page', get_wiki_page.get_hint_page),
    url('(.*)', get_wiki_page.get)
]
