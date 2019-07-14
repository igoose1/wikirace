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
    FixedGameTaskGenerator,\
    GameTypes
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm
from .models import MultiplayerPair, Game
from random import choice
from django.db.models import ExpressionWrapper, F, fields


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
        except Exception:
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


def get_game_task_generator(difficulty, prevars):
    if difficulty == GameTypes.random:
        return RandomGameTaskGenerator(prevars.zim_file, prevars.graph)
    else:
        return DifficultGameTaskGenerator(difficulty)


def generate_game(prevars):
    settings = get_settings(
        prevars.request.session.get('settings', dict())
    )

    if settings.get('difficulty', None) is None:
        return HttpResponseRedirect('/'), False

    if isinstance(settings['difficulty'], int):
        prevars.request.session['settings'] = get_settings(dict())
        return HttpResponseBadRequest(), False

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
    return HttpResponseRedirect('/' + prevars.game_operator.current_page.url), True


@load_prevars
def get_start(prevars):
    response, _ = generate_game(prevars)
    return response


@requires_game
def get_continue(prevars):
    return HttpResponseRedirect('/' + prevars.game_operator.current_page.url)


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
        if prevars.game_operator.game.multiplayer is None:
            return winpage(prevars)
        else:
            return get_multiplayer_results(prevars)

    game_id = None
    if prevars.game_operator.game.multiplayer is not None:
        game_id = prevars.game_operator.game.multiplayer.game_id

    template = loader.get_template('wiki/page.html')
    context = {
        'title': article.title,
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'wiki_content': article.content.decode(),
        'history_empty': prevars.game_operator.is_history_empty,
        'game_id': game_id
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


def guid(length):
    g, s = ('аоиеуюя', 'бвгджзклмнпрстфхц')
    return ''.join([choice(g if i % 2 else s) for i in range(length)])


def generate_multiplayer(prevars):
    multiplayer = None
    counter = 0
    while True:
        gid = guid(5 + counter // 10)
        try:
            multiplayer = MultiplayerPair.objects.create(
                from_page_id=prevars.game_operator.game.start_page_id,
                to_page_id=prevars.game_operator.game.end_page_id,
                game_id=gid
            )
            break
        except Exception:
            pass
        finally:
            counter += 1
    prevars.game_operator.game.multiplayer = multiplayer


@load_prevars
def get_multiplayer_generate(prevars):
    response, state = generate_game(prevars)
    if state:
        generate_multiplayer(prevars)
    return response


@load_prevars
def get_multiplayer_join(prevars):
    game_id = prevars.request.GET.get('id', '')
    try:
        multiplayer = MultiplayerPair.objects.get(game_id=game_id)
    except Exception:
        return HttpResponseBadRequest()

    prevars.game_operator = GameOperator.create_game(
        FixedGameTaskGenerator(
            multiplayer.from_page_id,
            multiplayer.to_page_id
        ),
        prevars.zim_file,
        prevars.graph
    )
    prevars.game_operator.game.multiplayer = multiplayer
    return HttpResponseRedirect('/' + prevars.game_operator.current_page.url)


@load_prevars
def get_multiplayer_results_page(prevars):
    game_id = prevars.request.GET.get('id', '')

    if prevars.session_operator is not None and game_id == '':
        return get_multiplayer_results(prevars)

    try:
        multiplayer = MultiplayerPair.objects.get(game_id=game_id)
    except Exception:
        return HttpResponseBadRequest()
    results_table = get_multiplayer_results_table(multiplayer, None)

    context = {
        'results_table': results_table,
    }
    template = loader.get_template('wiki/results_page.html')
    return HttpResponse(template.render(context, prevars.request))


def get_multiplayer_results_table(multiplayer, pk):
    games = multiplayer.game_set\
        .extra(where=['current_page_id == end_page_id'])\
        .order_by('steps').all()[:5]

    results_table = []
    for game in games:
        results_table.append({
            'name': game.game_id,
            'steps': game.steps,
            'is_me': game.pk == pk
        })
    print(results_table)
    return results_table


def get_multiplayer_results(prevars):
    if prevars.game_operator.game.multiplayer is None:
        return HttpResponseBadRequest()
    prevars.game_operator._game.save()
    results_table = get_multiplayer_results_table(
        prevars.game_operator.game.multiplayer,
        prevars.game_operator.game.pk
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
