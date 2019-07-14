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
    GameTypes
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm
from .PathReader import get_path
from .models import Turn


class PreVariables:
    def __init__(self, request):
        self.zim_file = None
        self.graph = None
        try:
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
        except:
            if self.zim_file is not None:
                self.zim_file.close()
            if self.graph is not None:
                self.graph.close()
            raise

    def close(self):
        self.zim_file.close()
        self.graph.close()


def load_prevars(func):
    def wrapper(request, *args, **kwargs):
        prevars = PreVariables(request)
        try:
            prevars.session_operator = prevars.request.session.get('operator', None)
            res = func(prevars, *args, **kwargs)
            if prevars.game_operator is not None and not prevars.game_operator.finished:
                prevars.request.session['operator'] = prevars.game_operator.serialize_game_operator()
            else:
                prevars.request.session['operator'] = None
        finally:
            prevars.close()
        return res

    return wrapper


def requires_game(func):
    def wrapper(prevars, *args, **kwargs):
        if prevars.session_operator is None:
            return HttpResponseRedirect('/')
        return func(prevars, *args, **kwargs)

    return load_prevars(wrapper)


def get_settings(settings_user):
    default = {'difficulty': GameTypes.random.value, 'name': 'no name'}
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
    NAME_LEN = 16

    difficulty = prevars.request.POST.get('difficulty', None)
    name = prevars.request.POST.get('name')

    if difficulty not in [el.value for el in GameTypes] or (isinstance(name, str) and len(name) > NAME_LEN):
        return HttpResponseBadRequest()

    prevars.request.session['settings'] = {
        'difficulty': GameTypes(difficulty).value,
        'name': name
    }
    return HttpResponse('Ok')


def get_game_task_generator(difficulty, prevars):
    if difficulty == GameTypes.random:
        return RandomGameTaskGenerator(prevars.zim_file, prevars.graph)
    else:
        return DifficultGameTaskGenerator(difficulty)


@load_prevars
def get_start(prevars):
    settings = get_settings(
        prevars.request.session.get('settings', dict())
    )

    if settings.get('difficulty', None) is None:
        return HttpResponseRedirect('/')

    if isinstance(settings['difficulty'], int):
        prevars.request.session['settings'] = get_settings(dict())
        return HttpResponseBadRequest()

    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes(
                settings['difficulty']
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
def show_path_page(prevars):
    page_id = prevars.game_operator.game.start_page_id
    start = prevars.zim_file[page_id].title
    our_path_index = list(map(int, prevars.game_operator.game.possible_path.split()))
    our_path = []
    for idx in our_path_index:
        our_path.append(prevars.zim_file[idx].title)
    user_path = [start]
    game_id = prevars.game_operator.game.game_id
    turns = Turn.objects.filter(game_id=game_id).order_by('time')
    for turn in turns:
        page_id = turn.to_page_id
        user_path.append(prevars.zim_file[page_id].title)
    context = {
        'from': our_path[0],
        'our_path': our_path[1:],
        'user_path': user_path[1:],
    }
    template = loader.get_template('wiki/show_path_page.html')
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
