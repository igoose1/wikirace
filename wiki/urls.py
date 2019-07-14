from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from . import get_wiki_page


urlpatterns = [
    path('admin', admin.site.urls),
    url('^$', get_wiki_page.get_main_page),
    url('feedback', get_wiki_page.get_feedback_page),
    url('game_start', get_wiki_page.get_start),
    url('custom_game/([0-9])', get_wiki_page.custom_game_start),
    url('custom_game/(.*)', get_wiki_page.get),
    url('continue', get_wiki_page.get_continue),
    url('back', get_wiki_page.get_back),
    url('hint_page', get_wiki_page.get_hint_page),
    url('set_settings', get_wiki_page.change_settings),
    url('add_game', get_wiki_page.add_game),
    url('(.*)', get_wiki_page.get)
]
