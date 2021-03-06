from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path
from . import get_wiki_page


urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$', get_wiki_page.get_main_page),
    url('^feedback', get_wiki_page.get_feedback_page),
    path('join_game/<str:multiplayer_key>', get_wiki_page.join_game_by_key),
    path('results_of_game/<str:multiplayer_key>', get_wiki_page.show_results_table),
    path('results_of_trial/<str:trial_id>', get_wiki_page.show_trial_results_table),
    url('^choose_custom_game', get_wiki_page.choose_custom_game),
    path('custom_game_start/<int:trial_id>', get_wiki_page.custom_game_start),
    url('^game_random_start', get_wiki_page.get_random_start),
    url('^game_start', get_wiki_page.get_start),
    url('^continue', get_wiki_page.get_continue),
    url('^back', get_wiki_page.get_back),
    url('^A/hint_page', get_wiki_page.get_hint_page),
    url('^show_path_page', get_wiki_page.show_path_page),
    url('^set_settings', get_wiki_page.change_settings),
    # url('^set_name', get_wiki_page.change_name),
    url('^surrender', get_wiki_page.surrender),
    url('^endpage', get_wiki_page.end_page),
    url('^login', get_wiki_page.get_login_page),
    url('^global_rating', get_wiki_page.get_global_rating_page),
    re_path(r'^(?P<title_name>(((?!admin).*)|(admin(?!\/).+)))$', get_wiki_page.get)
]
