from django.http import HttpResponse, \
    HttpResponseRedirect, \
    HttpResponseNotFound, \
    HttpResponseBadRequest
from django.conf import settings
from django.template import loader
from django.utils import timezone
from django.shortcuts import get_object_or_404

from . import inflection
from .GameOperator import GameOperator,\
    DifficultGameTaskGenerator,\
    RandomGameTaskGenerator,\
    FixedGameTaskGenerator,\
    TrialGameTaskGenerator,\
    GameTypes
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm
from .models import MultiplayerPair, Game, Turn
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404
from .PathReader import get_path
from wiki.file_holder import file_holder
from .models import Trial


@file_holder
class PreVariables:
    def __init__(self, request):
        self.save_operator = True
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
        if self.game_operator is not None:
            session = Session.objects.get(session_key=request.session.session_key)
            self.game_operator.game.session = session
            self.game_operator.game.session_key = session.session_key
        self.session_operator = None
        self.request = request


def load_prevars(func):
    def wrapper(request, *args, **kwargs):
        prevars = PreVariables(request)
        try:
            prevars.session_operator = prevars.request.session.get('operator', None)
            res = func(prevars, *args, **kwargs)
            if prevars.save_operator:
                finished = True
                serialized_operator = None
                if prevars.game_operator is not None:
                    serialized_operator = prevars.game_operator.serialize_game_operator()
                    finished = prevars.game_operator.finished

                if not finished:
                    prevars.request.session['operator'] = serialized_operator
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


def get_game_task_generator(difficulty, prevars, trial=None):
    if difficulty == GameTypes.random:
        return RandomGameTaskGenerator(prevars.zim_file, prevars.graph)
    elif difficulty == GameTypes.trial:
        return TrialGameTaskGenerator(trial)
    else:
        return DifficultGameTaskGenerator(difficulty)


def generate_game(prevars):
    settings = get_settings(
        prevars.request.session.get('settings', dict())
    )

    if settings.get('difficulty', None) is None:
        return False

    if isinstance(settings['difficulty'], int):
        prevars.request.session['settings'] = get_settings(dict())
        return False

    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes(
                settings['difficulty']
            ),
            prevars,
        ),
        prevars.zim_file,
        prevars.graph
    )
    return True


def current_page_url_redirect(prevars):
    return HttpResponseRedirect('/' + prevars.game_operator.current_page.url)


@load_prevars
def get_start(prevars):
    is_generated = generate_game(prevars)
    if is_generated:
        response = current_page_url_redirect(prevars)
    else:
        response = HttpResponseRedirect('/')
    return response


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
    return current_page_url_redirect(prevars)


@requires_game
def get_back(prevars):
    prevars.game_operator.jump_back()
    return current_page_url_redirect(prevars)


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
    our_path = [
        prevars.zim_file[idx].title for idx in prevars.game_operator.path
    ]
    if len(our_path) == 0:
        our_path = [start]
    user_path = [start]
    game_id = prevars.game_operator.game.game_id
    turns = Turn.objects.filter(game_id=game_id).order_by('time')

    user_path += [prevars.zim_file[turn.to_page_id].title for turn in turns]
    context = {
        'from': our_path[0],
        'our_path': our_path[1:],
        'user_path': user_path[1:],
    }
    template = loader.get_template('wiki/show_path_page.html')
    return HttpResponse(template.render(context, prevars.request))


def get_win_page(prevars):
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
        'name': settings_user['name'],
        'game_id': prevars.game_operator.game.game_id
    }
    template = loader.get_template('wiki/win_page.html')
    return HttpResponse(template.render(context, prevars.request))


@requires_game
def get(prevars, title_name):
    article = prevars.zim_file[title_name].follow_redirect()
    if article.is_empty or article.is_redirecting:
        prevars.save_operator = False
        return HttpResponseNotFound()

    if article.namespace != ZIMFile.NAMESPACE_ARTICLE:
        prevars.save_operator = False
        return HttpResponse(article.content, content_type=article.mimetype)

    if not prevars.game_operator.is_jump_allowed(article):
        return current_page_url_redirect(prevars)
    prevars.game_operator.jump_to(article)

    if prevars.game_operator.finished:
        if prevars.game_operator.game.multiplayer is None:
            return get_win_page(prevars)
        else:
            return get_multiplayer_results(prevars)

    game_key = None
    if prevars.game_operator.game.multiplayer is not None:
        game_key = prevars.game_operator.game.multiplayer.game_key

    template = loader.get_template('wiki/game_page.html')
    context = {
        'title': article.title,
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'wiki_content': article.content.decode(),
        'history_empty': prevars.game_operator.is_history_empty,
        'game_id': game_key
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


def generate_multiplayer(prevars):
    multiplayer = MultiplayerPair.objects.create(
        game_pair = prevars.game_operator.game.game_pair
    )
    prevars.game_operator.game.multiplayer = multiplayer


@load_prevars
def get_multiplayer_generate(prevars):
    is_generated = generate_game(prevars)
    if is_generated:
        generate_multiplayer(prevars)
        response = current_page_url_redirect(prevars)
    else:
        response = HttpResponseRedirect('/')
    return response


def get_multiplayer_from_GET(request):
    game_key = request.GET.get('id', None)
    if game_key is None:
        return None
    multiplayer = get_object_or_404(MultiplayerPair, game_key=game_key)
    return multiplayer


@load_prevars
def get_multiplayer_join(prevars):
    multiplayer = get_multiplayer_from_GET(prevars.request)
    if multiplayer is None:
        return HttpResponseNotFound()

    prevars.game_operator = GameOperator.create_game(
        FixedGameTaskGenerator(
            multiplayer.game_pair
        ),
        prevars.zim_file,
        prevars.graph
    )
    prevars.game_operator.game.multiplayer = multiplayer
    return current_page_url_redirect(prevars)


@load_prevars
def get_multiplayer_results_page(prevars):
    multiplayer = get_multiplayer_from_GET(prevars.request)

    if prevars.session_operator is not None and multiplayer is None:
        return get_multiplayer_results(prevars)

    if multiplayer is None:
        return HttpResponseNotFound()

    results_table = get_multiplayer_results_table(
        multiplayer,
        prevars.request.session.session_key
    )

    context = {
        'results_table': results_table,
    }
    template = loader.get_template('wiki/results_page.html')
    return HttpResponse(template.render(context, prevars.request))


def get_multiplayer_results_table(multiplayer, session_key, top_n=5):
    games = multiplayer.game_set\
        .extra(where=["current_page_id == (SELECT end_page_id FROM 'wiki_gamepair' WHERE pair_id == game_pair_id LIMIT 1)"])\
        .order_by('steps').all()

    results_table = []
    used_keys = set()
    for game in games:
        if len(used_keys) == top_n:
            break

        game_session_key = game.session_key
        if game_session_key in used_keys:
            continue
        used_keys.add(game_session_key)
        if game.session is not None:
            session = game.session.get_decoded()
            used_keys.add(game_session_key)
        else:
            session = {'settings': {'name': 'expired'}}

        name = get_settings(session.get('settings', dict())).get('name', 'no name')

        results_table.append({
            'name': name,
            'steps': game.steps,
            'is_me': game_session_key == session_key
        })
    return results_table


def get_multiplayer_results(prevars):
    if prevars.game_operator.game.multiplayer is None:
        return HttpResponseBadRequest()
    prevars.game_operator._game.save()
    results_table = get_multiplayer_results_table(
        prevars.game_operator.game.multiplayer,
        prevars.request.session.session_key
    )
    context = {
        'results_table': results_table,
        'my_results': {
            'name': 'вы',
            'steps': prevars.game_operator.game.steps
        },
        'my_results_finished': prevars.game_operator.finished
    }
    template = loader.get_template('wiki/results_page.html')
    return HttpResponse(template.render(context, prevars.request))
