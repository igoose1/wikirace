from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from . import get_wiki_page


urlpatterns = [
    path('admin', admin.site.urls),
    path('admin/', admin.site.urls),
    url('^$', get_wiki_page.get_main_page),
    url('feedback', get_wiki_page.get_feedback_page),
    path('join_game/<str:multiplayer_key>', get_wiki_page.join_game_by_key),
    path('results_of_game/<str:multiplayer_key>', get_wiki_page.show_results_table),
    url('choose_custom_game', get_wiki_page.choose_custom_game),
    path('custom_game_start/<int:trial_id>', get_wiki_page.custom_game_start),
    url('game_random_start', get_wiki_page.get_random_start),
    url('game_start', get_wiki_page.get_start),
    url('continue', get_wiki_page.get_continue),
    url('back', get_wiki_page.get_back),
    url('hint_page', get_wiki_page.get_hint_page),
    url('show_path_page', get_wiki_page.show_path_page),
    url('set_settings', get_wiki_page.change_settings),
    url('surrender', get_wiki_page.surrender),
    url('(.*)', get_wiki_page.get)
]
