from django.conf.urls import url

from . import get_wiki_page

"""
    
    """
urlpatterns = [
    url('main', get_wiki_page.get_main_page),
    url('game_start', get_wiki_page.get_start),
    url('continue', get_wiki_page.get_continue),
    url('(.*)', get_wiki_page.get)
]
