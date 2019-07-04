from gevent import monkey
monkey.patch_all = lambda *_: None

from django.http import HttpResponse, Http404
from django.conf import settings

from django.template import loader


from .ZIMFile import MyZIMFile
from .GameOperator import GameOperator
from .GraphReader import GraphReader
from wiki.models import Game
from var_init import *


def get(request, title_name):
    game_operator = GameOperator(zim, graph)
    if request.session.get('operator', None) is None or input('TYPE') == 's':
        # начало игры
        game_operator.initialize_game()
        Game.objects.create(session_id=request.session.session_key,
                            first=game_operator.current_page_id,
                            last=game_operator.end_page_id,
                            steps=0,
							ended=False)
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
        curr_game = Game.objects.filter(session_id=request.session.session_key)[0]
        curr_game.steps = request.session['steps']
        curr_game.ended = next_page_result
        curr_game.commit()
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
