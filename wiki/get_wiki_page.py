from gevent import monkey
monkey.patch_all = lambda *_: None

import requests

from django.http import HttpResponse, Http404
from django.conf import settings

from django.template import loader


from .ZIMFile import MyZIMFile
from .GameOperator import GameOperator
from .GraphReader import GraphReader


def get(request, title_name):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph_reader = GraphReader(
        settings.GRAPH_OFFSET_PATH,
        settings.GRAPH_EDGES_PATH
    )
    game_operator = GameOperator(zim_file, graph_reader)

    if request.session.get('steps', None) is None:
        game_operator.initialize_game()
        request.session['steps'] = 0
        request.session['operator'] = game_operator.save()
        return HttpResponse('New game!')
    else:
        game_operator.load(request.session['operator'])

    #wiki_page_request = requests.get(settings.WIKI_MIRROR_HOST + title_name)

    content = zim_file.get_by_url(f'/{title_name}')
    if content is None:
        raise Http404()

    data, namespace, mime_type = content

    if namespace == 'A':
        request.session['steps'] += 1
        next_page_result = game_operator.next_page(f'/{title_name}')
        request.session['operator'] = game_operator.save()

        if next_page_result:
            return HttpResponse('You\'ve won!')
        elif next_page_result is None:
            return HttpResponse('Something went wrong...')

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
            content_type=mime_type
        )

    return HttpResponse(
        data,
        content_type=mime_type
    )
 
