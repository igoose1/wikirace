from django.conf.urls import url

from . import get_wiki_page


urlpatterns = [
    url('^$', get_wiki_page.get_main_page),
    url('game_start', get_wiki_page.get_start),
    url('continue', get_wiki_page.get_continue),
    url('back', get_wiki_page.get_back),
    url('hint_page', get_wiki_page.get_hint_page),
    url('set_settings', get_wiki_page.change_settings),
    url('(.*)', get_wiki_page.get)
]
