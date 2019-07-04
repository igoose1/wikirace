from django.conf.urls import url

from . import get_wiki_page_template


urlpatterns = [
    url('(.*)', get_wiki_page_template.get)
]
