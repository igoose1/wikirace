# from django.
from django.http import HttpResponse
from django.conf import settings

import requests


def get(request, title_name):
    return HttpResponse(
        requests.get(settings.WIKI_MIRROR_HOST + title_name).text
    )
    # return HttpResponse(title_name)
