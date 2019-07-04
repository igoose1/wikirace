from gevent import monkey

monkey.patch_all = lambda *_: None

from django.http import HttpResponse, Http404
from django.conf import settings

from django.template import loader

from .ZIMFile import MyZIMFile
from .GameOperator import GameOperator
from .GraphReader import GraphReader
from wiki.models import Game
import re


def get(request, title_name):
    zim_file = MyZIMFile(settings.WIKI_DATA)

    content = zim_file.get_by_url('/' + title_name)
    if content is None:
        return HttpResponse(Http404("NOT FOUND"))

    data, namespace, mime_type = content

    if namespace == 'A':
        graph = GraphReader(settings.GRAPH_DIR + '/offset_all', settings.GRAPH_DIR + '/edges_all')

        game_operator = GameOperator(zim_file, graph)
        if request.session.get('operator', None) is None:
            # начало игры
            game_operator.initialize_game()
            request.session['operator'] = game_operator.save()

            return HttpResponse('New game!')
        else:
            game_operator.load(request.session['operator'])
            print(request.session.session_key)
            curr_game = Game.objects.update_or_create(
                session_id=request.session.session_key,
                first=game_operator.start_page_id,
                ended=game_operator.game_finished,
                last=game_operator.end_page_id,
                steps=game_operator.steps,
            )[0]
            print(curr_game)
        next_page_result = game_operator.next_page('/' + title_name)
        curr_game = Game.objects.filter(session_id=request.session.session_key)[0]
        curr_game.steps = game_operator.steps
        curr_game.ended = next_page_result
        curr_game.save()
        request.session['operator'] = game_operator.save()

        if next_page_result:
            return HttpResponse('You\'ve won!')
        elif next_page_result is None:
            return HttpResponse('Something went wrong...')

        template = loader.get_template('wiki/frame.html')
        counter = game_operator.steps
        context = {
            'from': zim_file.read_directory_entry_by_index(game_operator.start_page_id)['title'],
            'to': zim_file.read_directory_entry_by_index(game_operator.end_page_id)['title'],
            'counter': counter,
            'wiki_content': data.decode('utf-8'),
        }
        return HttpResponse(
            template.render(context, request),
            content_type=mime_type
        )

    return HttpResponse(
        data,
        content_type=mime_type
    )


def parse_article(article: str):
    m = re.search(r"<body.*?>(.*?)</body>", article, re.S)
    body = m.group(1) if m else ""
    return body
