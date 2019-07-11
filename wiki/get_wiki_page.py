from django.http import HttpResponse,\
    HttpResponseRedirect,\
    HttpResponseNotFound,\
    HttpResponseBadRequest
from django.conf import settings
from django.template import loader
from django.utils import timezone

from . import inflection
from .GameOperator import GameOperator,\
    DifficultGameTaskGenerator,\
    RandomGameTaskGenerator,\
    Difficulties
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
        self.game_operator = GameOperator.deserialize_game_operator(
            request.session.get('operator', None),
            self.zim_file,
            self.graph,
            'loadtesting' in request.GET and request.META['REMOTE_ADDR'].startswith('127.0.0.1')
        )
        self.session_operator = None
        self.request = request


def load_prevars(func):
    def wrapper(request, *args, **kwargs):
        prevars = PreVariables(request)
        prevars.session_operator = prevars.request.session.get('operator')
        res = func(prevars, *args, **kwargs)
        if prevars.game_operator is not None:
            prevars.request.session['operator'] = prevars.game_operator.serialize_game_operator()
        else:
            prevars.request.session['operator'] = None
        return res

    return wrapper


def requires_game(func):
    def wrapper(prevars, *args, **kwargs):
        if prevars.session_operator is None:
            return HttpResponseRedirect('/')
        return func(prevars, *args, **kwargs)

    return load_prevars(wrapper)


def get_settings(settings_user):
    default = {'difficulty': Difficulties.random.value, 'name': 'no name'}
    for key in default.keys():
        settings_user[key] = settings_user.get(key, default[key])
    return settings_user


@load_prevars
def get_main_page(prevars):
    template = loader.get_template('wiki/start_page.html')
    context = {
        'is_playing': prevars.session_operator is not None and not prevars.game_operator.finished,
        'settings': get_settings(
            prevars.request.session.get('settings', dict())
        )
    }
    return HttpResponse(template.render(context, prevars.request))


@load_prevars
def change_settings(prevars):
    difficulty = prevars.request.POST.get('difficulty', None)
    name = prevars.request.POST.get('name')

    if difficulty not in [el.value for el in Difficulties] or (isinstance(name, str) and len(name) > 16):
        return HttpResponseBadRequest()

    prevars.request.session['settings'] = {
        'difficulty': Difficulties(difficulty).value,
        'name': name
    }
    return HttpResponse('Ok')


def get_game_task_generator(difficulty, prevars):
    if difficulty == Difficulties.random:
        return RandomGameTaskGenerator(prevars.zim_file, prevars.graph)
    else:
        return DifficultGameTaskGenerator(difficulty)


@load_prevars
def get_start(prevars):
    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            Difficulties(
                get_settings(
                    prevars.request.session.get('settings', dict())
                )['difficulty']
            ),
            prevars
        ),
        prevars.zim_file,
        prevars.graph
    )
    return HttpResponseRedirect(prevars.game_operator.current_page.url)


@requires_game
def get_continue(prevars):
    return HttpResponseRedirect(prevars.game_operator.current_page.url)


@requires_game
def get_back(prevars):
    prevars.game_operator.jump_back()
    return HttpResponseRedirect(prevars.game_operator.current_page.url)


@requires_game
def get_hint_page(prevars):
    article = prevars.game_operator.last_page

    template = loader.get_template('wiki/hint_page.html')
    context = {
        'content': article.content.decode(),
    }
    return HttpResponse(template.render(context, prevars.request))


@requires_game
def winpage(prevars):
    settings_user = get_settings(
        prevars.request.session.get('settings', dict())
    )
    context = {
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'move_end': inflection.mupltiple_suffix(
            prevars.game_operator.game.steps
        ),
        'name': settings_user['name']
    }
    template = loader.get_template('wiki/win_page.html')
    prevars.game_operator.game = None
    return HttpResponse(template.render(context, prevars.request))


@requires_game
def get(prevars, title_name):
    article = prevars.zim_file[title_name].follow_redirect()
    if article.is_empty or article.is_redirecting:
        return HttpResponseNotFound()

    if article.namespace != ZIMFile.NAMESPACE_ARTICLE:
        return HttpResponse(article.content, content_type=article.mimetype)

    if not prevars.game_operator.is_jump_allowed(article):
        return HttpResponseRedirect(
            prevars.game_operator.current_page.url
        )
    prevars.game_operator.jump_to(article)

    if prevars.game_operator.finished:
        return winpage(prevars.request)

    template = loader.get_template('wiki/page.html')
    context = {
        'title': article.title,
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'wiki_content': article.content.decode(),
        'history_empty': prevars.game_operator.is_history_empty
    }
    return HttpResponse(
        template.render(context, prevars.request),
        content_type=article.mimetype
    )


@load_prevars
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
