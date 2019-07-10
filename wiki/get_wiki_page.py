from django.http import HttpResponseServerError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.utils import timezone

from .GameOperator import *
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm


def get(request, title_name):
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)

    article = zim_file[title_name]

    if article.namespace == ZIMFile.NAMESPACE_ARTICLE:
        article = article.follow_redirect()
        graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)

        if request.session.get('operator', None) is None:
            return HttpResponseRedirect('/')

        game_operator = GameOperator.deserialize_game_operator(
            request.session['operator'],
            zim_file,
            graph,
            "loadtesting" in request.GET and request.META["REMOTE_ADDR"].startswith("127.0.0.1")
        )

        if game_operator is None:
            return HttpResponseRedirect('/')

        if not game_operator.is_jump_allowed(article):
            return HttpResponseRedirect(
                game_operator.current_page.url
            )

        game_operator.jump_to(article)
        request.session['operator'] = game_operator.serialize_game_operator()

        if game_operator.finished:
            return winpage(request)

        template = loader.get_template('wiki/page.html')
        context = {
            'title': article.title,
            'from': game_operator.first_page.title,
            'to': game_operator.last_page.title,
            'counter': game_operator.game.steps,
            'wiki_content': article.content.decode('utf-8'),
            'history_empty': game_operator.is_history_empty
        }
        return HttpResponse(
            template.render(context, request),
            content_type=article.mimetype
        )

    return HttpResponse(
        article.content,
        content_type=article.mimetype
    )


def get_start(request):
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator.create_game(get_game_task_generator(get_settings(request)['difficulty']), zim_file,
                                             graph)
    request.session['operator'] = game_operator.serialize_game_operator()
    return HttpResponseRedirect(
        zim_file[game_operator.game.current_page_id].url
    )


def get_back(request):
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    game_operator = GameOperator.deserialize_game_operator(session_operator, zim_file, graph)
    game_operator.jump_back()
    request.session['operator'] = game_operator.serialize_game_operator()
    return HttpResponseRedirect(
        zim_file[game_operator.game.current_page_id].url
    )


def get_continue(request):
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    game_operator = GameOperator.deserialize_game_operator(session_operator, zim_file, graph)
    return HttpResponseRedirect(
        zim_file[game_operator.game.current_page_id].url
    )


def winpage(request):
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    session_operator = request.session.get('operator', None)
    if session_operator is None:
        return HttpResponseRedirect('/')
    game_operator = GameOperator.deserialize_game_operator(request.session['operator'], zim_file, graph)
    ending = ''
    if game_operator.game.steps % 10 == 1 and game_operator.game.steps % 100 != 11:
        pass
    elif game_operator.game.steps % 10 in [2, 3, 4] and game_operator.game.steps % 100 not in [12, 13, 14]:
        ending = 'а'
    else:
        ending = 'ов'
    settings_user = get_settings(request)
    context = {
        'from': zim_file[game_operator.game.start_page_id].title,
        'to': zim_file[game_operator.game.end_page_id].title,
        'counter': game_operator.game.steps,
        'move_end': ending,
        'name': settings_user['name']
    }
    template = loader.get_template('wiki/win_page.html')
    request.session['operator'] = None
    return HttpResponse(
        template.render(context, request),
    )


def get_main_page(request) -> HttpResponse:
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    template = loader.get_template('wiki/start_page.html')
    session_operator = request.session.get('operator', None)
    game_operator = GameOperator.deserialize_game_operator(session_operator, zim_file, graph)
    if game_operator is None:
        is_playing = False
    else:
        is_playing = not game_operator.finished

    context = {
        'is_playing': is_playing,
        'settings': get_settings(request)
    }
    return HttpResponse(template.render(context, request))


def get_hint_page(request):
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)

    if request.session.get('operator', None) is None:
        return HttpResponseRedirect('/')
    game_operator = GameOperator.deserialize_game_operator(request.session['operator'], zim_file, graph)

    content = zim_file[game_operator.game.end_page_id].content

    context = {
        'content': content.decode('utf-8'),
    }

    template = loader.get_template('wiki/hint_page.html')
    return HttpResponse(template.render(context, request))


def get_difficulty_level_by_name(name):
    if name == 'random':
        return RANDOM_GAME_TYPE
    if name == 'easy':
        return DIFFICULT_EASY
    if name == 'medium':
        return DIFFICULT_MEDIUM
    if name == 'hard':
        return DIFFICULT_HARD
    return None


def get_game_task_generator(diff):
    zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    graph = GraphReader(settings.GRAPH_OFFSET_PATH, settings.GRAPH_EDGES_PATH)
    if diff == RANDOM_GAME_TYPE:
        return RandomGameTaskGenerator(zim_file, graph)
    else:
        return DifficultGameTaskGenerator(diff)


def default_settings():
    return {'difficulty': DIFFICULT_EASY, 'name': 'no name'}


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
        return HttpResponseServerError()
    request.session['settings'] = {'difficulty': diff_id, 'name': name}
    return HttpResponse("OK")


def get_feedback_page(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        post = form.save()
        post.time = timezone.now()
        post.save()
        return HttpResponseRedirect('/')
    else:
        form = FeedbackForm()

    context = {
        'form': form,
    }
    template = loader.get_template('wiki/feedback_page.html')
    return HttpResponse(template.render(context=context, request=request))
