from django.http import HttpResponse,\
    HttpResponseRedirect,\
    HttpResponseNotFound,\
    HttpResponseBadRequest
from django.conf import settings
from django.template import loader
from django.utils import timezone

from . import declension
from .GameOperator import GameOperator
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm


class PreVariables:
    def __init__(self, request):
        self.zim_file = ZIMFile(
            settings.WIKI_ZIMFILE_PATH,
            settings.WIKI_ARTICLES_INDEX_FILE_PATH
        )
        self.graph = GraphReader(
            settings.GRAPH_OFFSET_PATH,
            settings.GRAPH_EDGES_PATH
        )
        self.game_operator = GameOperator(self.zim_file, self.graph)
        self.session_operator = None
        self.request = request


def requires_graph(func):
    def wrapper(request, *args, **kwargs):
        prevars = PreVariables(request)
        prevars.session_operator = prevars.request.session['operator']
        res = func(prevars, *args, **kwargs)
        if prevars.game_operator.game is not None:
            prevars.request.session['operator'] = prevars.game_operator.save()
        else:
            prevars.request.session['operator'] = None
        return res

    return wrapper


def requires_game(func):
    def wrapper(prevars, *args, **kwargs):
        session_operator = prevars.request.session.get('operator', None)
        if session_operator is None:
            return HttpResponseRedirect('/')
        prevars.game_operator.load(session_operator)
        return func(prevars, *args, **kwargs)

    return wrapper


def get_settings(settings_user):
    default = {'difficulty': -1, 'name': 'no name'}
    for key in default.keys():
        settings_user[key] = settings_user.get(key, default[key])
    return settings_user


@requires_graph
def get_main_page(prevars):
    template = loader.get_template('wiki/start_page.html')
    context = {
        'is_playing': prevars.session_operator and not prevars.session_operator[2],
        'settings': get_settings(
            prevars.request.session.get('settings')
        )
    }
    return HttpResponse(template.render(context, prevars.request))


@requires_graph
def change_settings(prevars):
    difficulty = prevars.request.POST.get('difficulty', None)
    name = prevars.request.POST.get('name')

    difficulty_names = ('random', 'easy', 'medium', 'hard')
    if difficulty not in difficulty_names\
            or (isinstance(name, str) and len(name) > 16):
        return HttpResponseBadRequest()

    prevars.request.session['settings'] = {
        'difficulty': difficulty_names.index(difficulty) - 1,
        'name': name
    }
    return HttpResponse('Ok')


@requires_graph
def get_start(prevars):
    prevars.game_operator.initialize_game(
        get_settings(
            prevars.request.session.get('settings', dict())
        )['difficulty']
    )
    return HttpResponseRedirect(
        prevars.zim_file[prevars.game_operator.current_page_id].url
    )


@requires_graph
@requires_game
def get_continue(prevars):
    return HttpResponseRedirect(
        prevars.zim_file[prevars.game_operator.current_page_id].url
    )


@requires_graph
@requires_game
def get_back(prevars):
    prevars.game_operator.prev_page()
    return HttpResponseRedirect(
        prevars.zim_file[prevars.game_operator.current_page_id].url
    )


@requires_graph
@requires_game
def get_hint_page(prevars):
    article = prevars.zim_file[prevars.game_operator.end_page_id]

    template = loader.get_template('wiki/hint_page.html')
    context = {
        'content': article.content.decode(),
    }
    return HttpResponse(template.render(context, prevars.request))


@requires_graph
@requires_game
def winpage(prevars):
    settings_user = get_settings(
        prevars.request.session.get('settings', dict())
    )
    context = {
        'from': prevars.zim_file[
            prevars.game_operator.start_page_id
        ].title,
        'to': prevars.zim_file[
            prevars.game_operator.end_page_id
        ].title,
        'counter': prevars.game_operator.steps,
        'move_end': declension.mupltiple_suffix(
            prevars.game_operator.steps
        ),
        'name': settings_user['name']
    }
    template = loader.get_template('wiki/win_page.html')
    prevars.game_operator.game = None
    return HttpResponse(
        template.render(context, prevars.request),
    )


@requires_graph
@requires_game
def get(prevars, title_name):
    article = prevars.zim_file[title_name].follow_redirect()
    if article.is_empty or article.is_redirecting:
        return HttpResponseNotFound()

    if article.namespace != ZIMFile.NAMESPACE_ARTICLE:
        return HttpResponse(article.content, content_type=article.mimetype)

    prevars.game_operator.load_testing = (
        "loadtesting" in prevars.request.GET and prevars.request.META["REMOTE_ADDR"].startswith("127.0.0.1")
    )

    next_page_result = prevars.game_operator.next_page('/' + title_name)

    if next_page_result:
        return winpage(prevars.request)
    elif next_page_result is None:
        return HttpResponseRedirect(
            prevars.zim_file[prevars.game_operator.current_page_id].url
        )

    template = loader.get_template('wiki/page.html')
    context = {
        'title': prevars.zim_file[
            prevars.game_operator.current_page_id
        ].title,
        'from': prevars.zim_file[
            prevars.game_operator.start_page_id
        ].title,
        'to': prevars.zim_file[
            prevars.game_operator.end_page_id
        ].title,
        'counter': prevars.game_operator.steps,
        'wiki_content': prevars.zim_file[
            prevars.game_operator.current_page_id
        ].content.decode(),
        'history_empty': prevars.game_operator.is_history_empty()
    }
    return HttpResponse(
        template.render(context, prevars.request),
        content_type=article.mimetype
    )


@requires_graph
def get_feedback_page(prevars):
    if prevars.request.method == "POST":
        form = FeedbackForm(prevars.request.POST).save()
        form.time = timezone.now()
        form.save()
        return HttpResponseRedirect('/')
    else:
        form = FeedbackForm()

    context = {
        'form': form,
    }
    template = loader.get_template('wiki/feedback_page.html')
    return HttpResponse(template.render(context, prevars.request))
