from django.http import HttpResponse
from django.conf import settings

from django.template import loader

import requests


def get(request, title_name):
    if request.session.get('steps', None) is None:
        request.session['steps'] = 0
        return HttpResponse('New game!')

    wiki_page_request = requests.get(settings.WIKI_MIRROR_HOST + title_name)

    if wiki_page_request.ok and\
            wiki_page_request.headers['content-type'] == 'text/html':
        request.session['steps'] += 1
        template = loader.get_template('wiki/frame.html')
        _from = 'start_page'
        to = 'finish_page'
        counter = request.session['steps']
        context = {
            'from': _from,
            'to': to,
            'counter': counter,
        }
        return HttpResponse(
            template.render(context, request),
            content_type=wiki_page_request.headers['content-type'],
            status=wiki_page_request.status_code
        )

    return HttpResponse(
        wiki_page_request.content,
        content_type=wiki_page_request.headers['content-type'],
        status=wiki_page_request.status_code
    )
