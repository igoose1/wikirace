from django.shortcuts import get_object_or_404
from django.http import HttpResponse,\
    HttpResponseRedirect,\
    HttpResponseNotFound,\
    HttpResponseBadRequest,\
    Http404
from django.conf import settings
from django.template import loader
from django.utils import timezone
from . import inflection
from .GameOperator import GameOperator,\
    DifficultGameTaskGenerator,\
    RandomGameTaskGenerator,\
    TrialGameTaskGenerator,\
    GameTypes,\
    ByIdGameTaskGenerator
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm
from .PathReader import get_path
from .models import Turn, \
    Trial
from wiki.file_holder import file_holder
from .models import Trial


@file_holder
class PreVariables:
    def __init__(self, request):
        self.zim_file = self._add_file(ZIMFile(
            settings.WIKI_ZIMFILE_PATH,
            settings.WIKI_ARTICLES_INDEX_FILE_PATH
        ))
        self.graph = self._add_file(GraphReader(
            settings.GRAPH_OFFSET_PATH,
            settings.GRAPH_EDGES_PATH
        ))
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
        try:
            prevars.session_operator = prevars.request.session.get('operator', None)
            res = func(prevars, *args, **kwargs)
            if prevars.game_operator is not None:
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
    default = {'difficulty': GameTypes.easy.value, 'name': 'no name'}
    for key in default.keys():
        settings_user[key] = settings_user.get(key, default[key])
    return settings_user


@load_prevars
def get_main_page(prevars):
    template = loader.get_template('wiki/start_page.html')
    trial_list = Trial.objects.all()
    context = {
        'is_playing': prevars.session_operator is not None and not prevars.game_operator.finished,
        'settings': get_settings(
            prevars.request.session.get('settings', dict())
        ),
        'trial_list': trial_list,
    }
    return HttpResponse(template.render(context, prevars.request))


@load_prevars
def change_settings(prevars):
    name_len = 16

    difficulty = prevars.request.POST.get('difficulty', None)
    name = prevars.request.POST.get('name')
    if difficulty not in GameTypes or (isinstance(name, str) and len(name) > name_len):
        return HttpResponseBadRequest()

    settings = prevars.request.session.get('settings', dict())
    settings['name'] = name
    if difficulty in [el.value for el in GameTypes]:
        settings['difficulty'] = GameTypes(difficulty).value
    prevars.request.session['settings'] = settings
    return HttpResponse('Ok')


def get_game_task_generator(difficulty, prevars, trial=None, pair_id=None):
    if difficulty == GameTypes.random:
        return RandomGameTaskGenerator(prevars.zim_file, prevars.graph)
    elif difficulty == GameTypes.trial:
        return TrialGameTaskGenerator(trial)
    elif difficulty == GameTypes.by_id:
        if not pair_id:
            raise Http404()
        return ByIdGameTaskGenerator(pair_id)
    else:
        return DifficultGameTaskGenerator(difficulty)


@load_prevars
def get_start(prevars):
    settings = get_settings(
        prevars.request.session.get('settings', dict())
    )

    if isinstance(settings['difficulty'], int):
        settings = get_settings(dict())

    prevars.request.session['settings'] = settings

    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes(
                settings['difficulty']
            ),
            prevars,
        ),
        prevars.zim_file,
        prevars.graph,
    )
    return HttpResponseRedirect('/' + prevars.game_operator.current_page.url)


@load_prevars
def get_start_by_id(prevars, pair_id):
    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes.by_id,
            prevars,
            pair_id=pair_id,
        ),
        prevars.zim_file,
        prevars.graph,
    )
    return HttpResponseRedirect('/' + prevars.game_operator.current_page.url)


@load_prevars
def custom_game_start(prevars, trial_id):
    t = get_object_or_404(Trial.objects.all(), trial_id=trial_id)
    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes.trial,
            prevars,
            trial=t,
        ),
        prevars.zim_file,
        prevars.graph
    )
    return HttpResponseRedirect('/' + prevars.game_operator.current_page.url)


@load_prevars
def get_random_start(prevars):
    prevars.game_operator = GameOperator.create_game(
        RandomGameTaskGenerator(prevars.zim_file, prevars.graph),
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
    page_id = prevars.game_operator.start_page_id
    start = prevars.zim_file[page_id].title
    our_path = [
        prevars.zim_file[idx].title for idx in prevars.game_operator.path
    ]
    if len(our_path) == 0:
        our_path = [start]
    user_path = [start]

    game_id = prevars.game_operator.game_id
    turns = Turn.objects.filter(game_id=game_id).order_by('step')

    user_path += [prevars.zim_file[turn.to_page_id].title for turn in turns]
    context = {
        'from': our_path[0],
        'our_path': our_path[1:],
        'user_path': user_path[1:],
    }
    template = loader.get_template('wiki/show_path_page.html')
    return HttpResponse(template.render(context, prevars.request))


def get_end_page(prevars):
    settings_user = get_settings(
        prevars.request.session.get('settings', dict())
    )
    surrendered = prevars.game_operator.surrendered
    context = {
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'pair_id': prevars.game_operator.game_pair.pair_id,
        'move_end': inflection.mupltiple_suffix(
            prevars.game_operator.game.steps
        ),
        'name': settings_user['name'],
        'game_id': prevars.game_operator.game_id,
        'title_text': 'Победа' if not surrendered else 'Игра окончена'
    }
    template = loader.get_template('wiki/end_page.html')
    return HttpResponse(template.render(context, prevars.request))


@requires_game
def surrender(prevars):
    prevars.game_operator.surrender()
    return get_end_page(prevars)


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
        return get_end_page(prevars)

    template = loader.get_template('wiki/game_page.html')
    context = {
        'title': article.title,
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'pair_id': prevars.game_operator.game.game_pair.pair_id,
        'wiki_content': article.content.decode(),
        'history_empty': prevars.game_operator.is_history_empty,
    }
    return HttpResponse(
        template.render(context, prevars.request),
        content_type=article.mimetype
    )


@load_prevars
def choose_custom_game(prevars):
    trials = Trial.objects.all()
    template = loader.get_template('wiki/choose_custom_game.html')
    context = {
        'title': 'Выбери челлендж',
        'trials': trials
    }
    return HttpResponse(template.render(context, prevars.request))


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
