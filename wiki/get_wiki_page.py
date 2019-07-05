from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.template import loader

from .ZIMFile import MyZIMFile
from .GameOperator import GameOperator
from .GraphReader import GraphReader
from wiki.models import Game
import re


def get(request, title_name):
    print(title_name)
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)

    content = zim_file.get_by_url('/' + title_name)
    if content is None:
        return get_main_page(request)

    data, namespace, mime_type = content

    if namespace == 'A':
        print("HELLO")
        graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)

        game_operator = GameOperator(zim_file, graph)
        if request.session.get('operator', None) is None:
            print("HELLO")
            return get_main_page(request)
        else:
            game_operator.load(request.session['operator'])
            print(request.session.session_key)
        next_page_result = game_operator.next_page('/' + title_name)
        request.session['operator'] = game_operator.save()

        if next_page_result:
            return winpage(request)
        elif next_page_result is None:
            return HttpResponse('Something went wrong...')

        template = loader.get_template('wiki/page.html')
        counter = game_operator.steps
        context = {
            'title': zim_file.read_directory_entry_by_index(game_operator.current_page_id)['title'],
            'from': zim_file.read_directory_entry_by_index(game_operator.start_page_id)['title'],
            'to': zim_file.read_directory_entry_by_index(game_operator.end_page_id)['title'],
            'counter': counter,
            'wiki_content': zim_file.get_by_index(game_operator.current_page_id).data.decode('utf-8'),
        }
        return HttpResponse(
            template.render(context, request),
            content_type=mime_type
        )

    return HttpResponse(
        data,
        content_type=mime_type
    )


def get_start(request):
    print("INIT")
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator(zim_file, graph)
    game_operator.initialize_game()
    request.session['operator'] = game_operator.save()
    return HttpResponseRedirect(
        zim_file.read_directory_entry_by_index(game_operator.current_page_id)['url']
    )


def get_continue(request):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator(zim_file, graph)
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    game_operator.load(session_operator)
    context = {
        'from': zim_file.read_directory_entry_by_index(game_operator.start_page_id)['title'],
        'to': zim_file.read_directory_entry_by_index(game_operator.end_page_id)['title'],
        'counter': game_operator.steps,
        'wiki_content': zim_file.get_by_index(game_operator.current_page_id).data.decode('utf-8'),
    }
    return HttpResponse(
        loader.get_template("wiki/page.html").render(context, request),
    )


def winpage(request):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator(zim_file, graph)
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    game_operator.load(session_operator)
    context = {
        'from': zim_file.read_directory_entry_by_index(game_operator.start_page_id)['title'],
        'to': zim_file.read_directory_entry_by_index(game_operator.end_page_id)['title'],
        'counter': game_operator.steps
    }
    template = loader.get_template('wiki/win_page.html')
    return HttpResponse(
        template.render(context, request),
    )


def get_main_page(request) -> HttpResponse:
    template = loader.get_template('wiki/start_page.html')
    session_operator = request.session.get('operator', None)
    is_playing = False
    if (session_operator and not session_operator[2]):
        is_playing = True
    return HttpResponse(template.render({'is_playing': is_playing}, request))


def get_hint_page(request):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)

    game_operator = GameOperator(zim_file, graph)
    if request.session.get('operator', None) is None:
        print("HELLO")
        return get_main_page(request)
    else:
        game_operator.load(request.session['operator'])
        print(request.session.session_key)


    content = zim_file.get_by_index(game_operator.end_page_id)
    data, namespace, mime_type = content

    context = {
        'content': data.decode('utf-8'),
    }

    template = loader.get_template('wiki/hint_page.html')
    return HttpResponse(template.render(context, request))
