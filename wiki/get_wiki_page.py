from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.conf import settings

from django.template import loader

from .ZIMFile import MyZIMFile
from .GameOperator import GameOperator
from .GraphReader import GraphReader
from wiki.models import Game
import re
 

def get(request, title_name):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)

    content = zim_file.get_by_url('/' + title_name)
    if content is None:
        raise Http404()

    data, namespace, mime_type = content
    if namespace == 'A':
        graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)

        game_operator = GameOperator(zim_file, graph)
        game_operator.load_testing = ("loadtesting" in request.GET
                                      and request.META["REMOTE_ADDR"].startswith("127.0.0.1"))
        if request.session.get('operator', None) is None:
            return HttpResponseRedirect('/')
        game_operator.load(request.session['operator'])

        next_page_result = game_operator.next_page('/' + title_name)
        request.session['operator'] = game_operator.save()

        if next_page_result:
            return winpage(request)
        elif next_page_result is None:
            return HttpResponseRedirect(
                zim_file.read_directory_entry_by_index(game_operator.current_page_id)['url']
            )

        template = loader.get_template('wiki/page.html')
        context = {
            'title': zim_file.read_directory_entry_by_index(game_operator.current_page_id)['title'],
            'from': zim_file.read_directory_entry_by_index(game_operator.start_page_id)['title'],
            'to': zim_file.read_directory_entry_by_index(game_operator.end_page_id)['title'],
            'counter': game_operator.steps,
            'wiki_content': zim_file.get_by_index(game_operator.current_page_id).data.decode('utf-8'),
            'history_empty': game_operator.is_history_empty()
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
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator(zim_file, graph)
    difficulty = get_settings(request)['difficulty']
    game_operator.initialize_game(difficulty)
    request.session['operator'] = game_operator.save()
    return HttpResponseRedirect(
        zim_file.read_directory_entry_by_index(game_operator.current_page_id)['url']
    )


def get_back(request):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator(zim_file, graph)
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    game_operator.load(session_operator)
    game_operator.prev_page()
    request.session['operator'] = game_operator.save()
    return HttpResponseRedirect(
        zim_file.read_directory_entry_by_index(game_operator.current_page_id)['url']
    )
    
    
def get_continue(request):
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator(zim_file, graph)
    game_operator.load(session_operator)
    return HttpResponseRedirect(
        zim_file.read_directory_entry_by_index(game_operator.current_page_id)['url']
    )


def winpage(request):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator(zim_file, graph)
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    game_operator.load(session_operator)
    ending = ''
    if game_operator.steps % 10 == 1 and game_operator.steps % 100 != 11:
        pass
    elif game_operator.steps % 10 in [2, 3, 4] and game_operator.steps % 100 not in [12, 13, 14]:
        ending = 'а'
    else:
        ending = 'ов'
    settings_user = get_settings(request)
    context = {
        'from': zim_file.read_directory_entry_by_index(game_operator.start_page_id)['title'],
        'to': zim_file.read_directory_entry_by_index(game_operator.end_page_id)['title'],
        'counter': game_operator.steps,
        'move_end': ending,
        'name': settings_user['name']
    }
    template = loader.get_template('wiki/win_page.html')
    request.session['operator'] = None
    return HttpResponse(
        template.render(context, request),
    )


def get_main_page(request) -> HttpResponse:
    template = loader.get_template('wiki/start_page.html')
    session_operator = request.session.get('operator', None)
    is_playing = False
    if (session_operator and not session_operator[2]):
        is_playing = True
        
    context = {'is_playing': is_playing,
               'settings': get_settings(request)
                }
    return HttpResponse(template.render(context, request))


def get_hint_page(request):
    zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)

    game_operator = GameOperator(zim_file, graph)
    if request.session.get('operator', None) is None:
        return HttpResponseRedirect('/')
    game_operator.load(request.session['operator'])

    content = zim_file.get_by_index(game_operator.end_page_id)
    data, namespace, mime_type = content

    context = {
        'content': data.decode('utf-8'),
    }

    template = loader.get_template('wiki/hint_page.html')
    return HttpResponse(template.render(context, request))

def get_difficulty_level_by_name(name):
    if (name == 'random'):
        return -1
    if (name == 'easy'):
        return 0
    if (name == 'medium'):
        return 1
    if (name == 'hard'):
        return 2
    return None

def default_settings():
    return {'difficulty': -1, 'name': 'no name'}

def get_settings(request):
    default = default_settings()
    settings_user = request.session.get('settings', default)
    for key in default.keys():
        if key not in settings_user.keys():
            settings_user[key] = default[key]
    return settings_user

def change_settings(request):
    val = request.POST.get('difficulty', None)
    name = request.POST.get('name', 'no name')
    diff_id = get_difficulty_level_by_name(val)
    if diff_id is None or len(name) > 16:
        return HttpResponseServerError();
    request.session['settings'] = {'difficulty': diff_id, 'name': name}
    return HttpResponse("OK");

