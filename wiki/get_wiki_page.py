from django.http import HttpResponse
from django.conf import settings

import requests


def get(request, title_name):
    wiki_page_request = requests.get(settings.WIKI_MIRROR_HOST + title_name)
    return HttpResponse(
        wiki_page_request.content,
        content_type=wiki_page_request.headers['content-type']
    )
