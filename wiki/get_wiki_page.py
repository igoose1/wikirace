# from django.
from django.http import HttpResponse

import requests


def get(request, title_name):
    return HttpResponse(
        requests.get('http://10.5.200.206:9454/' + title_name).text
    )
    # return HttpResponse(title_name)
