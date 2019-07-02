from django.conf.urls import url

from . import get_wiki_page


urlpatterns = [
    url('(.+)', get_wiki_page.get)
]
