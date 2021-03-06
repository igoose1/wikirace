from django.shortcuts import get_object_or_404
from django.http import HttpResponse, \
    HttpResponseRedirect, \
    HttpResponseNotFound, \
    HttpResponseBadRequest, \
    Http404
from django.conf import settings
from django.template import loader
from django.utils import timezone
from django.db.models import Q
from . import inflection
from .GameOperator import GameOperator, \
    DifficultGameTaskGenerator, \
    RandomGameTaskGenerator, \
    TrialGameTaskGenerator, \
    MultipayerGameTaskGenerator, \
    ByIdGameTaskGenerator
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm
from .PathReader import get_path
from .models import Turn, \
    Trial, \
    GameTypes, GamePair, TrialType
from wiki.file_holder import file_holder
from .models import MultiplayerPair, UserSettings, Game, GameStats
import requests
from wiki import user_rating
import json


def redirect_to(page):
    if page[0] == '/' and settings.ROOT_PATH != "":
        return HttpResponseRedirect('/' + settings.ROOT_PATH.rstrip('/') + page)
    return HttpResponseRedirect(page)


@file_holder
class PreVariables:
    def __init__(self, request):
        self.settings = get_settings(request.session)
        if self.settings is None:
            return
        self.zim_file = self._add_file(ZIMFile(
            settings.WIKI_ZIMFILE_PATH,
            settings.WIKI_ARTICLES_INDEX_FILE_PATH
        ))
        self.graph = self._add_file(GraphReader(
            settings.GRAPH_OFFSET_PATH,
            settings.GRAPH_EDGES_PATH
        ))
        self.request = request
        sess = self.request.session.get('operator', {})
        if sess is None:
            sess = {}
        if self.settings.curr_game_id is not None:
            sess['game_id'] = self.settings.curr_game_id
            sess['history'] = json.loads(self.settings.history_json)

        self.game_operator = GameOperator.deserialize_game_operator(
            sess,
            self.zim_file,
            self.graph,
            self.settings,
            'loadtesting' in request.GET and request.META['REMOTE_ADDR'].startswith(
                '127.0.0.1'),
        )

    def redirect_to_curr_page(self):
        return redirect_to('/A/' + self.game_operator.current_page.url)


def load_prevars(func):
    def wrapper(request, *args, **kwargs):
        prevars = PreVariables(request)
        try:
            if prevars.settings is None:
                return redirect_to("/login")
            res = func(prevars, *args, **kwargs)
            prevars.settings.save()
            if prevars.game_operator is not None:
                sess = prevars.game_operator.serialize_game_operator()
                prevars.settings.curr_game_id = sess.get('game_id', None)
                prevars.settings.history_json = json.dumps(sess.get('history', ""))
                prevars.settings.save()
                prevars.request.session['operator'] = sess
            else:
                prevars.request.session['operator'] = None
        finally:
            prevars.close()
        return res

    return wrapper


def requires_game(func):
    def wrapper(prevars, *args, **kwargs):
        if prevars.game_operator is None:
            return redirect_to('/')
        return func(prevars, *args, **kwargs)

    return load_prevars(wrapper)


def requires_finished_game(func):
    def wrapper(prevars, *args, **kwargs):
        if not prevars.game_operator.finished:
            return prevars.redirect_to_curr_page()
        return func(prevars, *args, **kwargs)

    return requires_game(wrapper)


def get_settings(session):
    user_id = session.get('user_id', None)
    if UserSettings.objects.filter(user_id=user_id).count() == 0:
        if settings.VK_SECRET_KEY != '':
            return None
        else:
            user = UserSettings.objects.create(vk_id='', vk_access_token='')
            session['user_id'] = user.user_id
            user.save()
            return user

    user_settings = UserSettings.objects.get(user_id=user_id)

    return user_settings


@load_prevars
def get_main_page(prevars):

    template = loader.get_template('wiki/start_page.html')
    trial_list = list(Trial.objects.filter(type=TrialType.TRIAL))
    event_list = [x for x in Trial.objects.filter(type=TrialType.EVENT) if x.is_event_active]
    context = {
        'is_playing': prevars.game_operator is not None and not prevars.game_operator.finished,
        'settings': prevars.settings,
        'trial_list': trial_list,
        'event_list': event_list,
    }
    return HttpResponse(template.render(context, prevars.request))


@load_prevars
def change_settings(prevars):
    difficulty = prevars.request.POST.get('difficulty', None)
    if not any(t.value == difficulty for t in GameTypes):
        return HttpResponseBadRequest()

    prevars.settings.difficulty = GameTypes[difficulty]
    prevars.settings.save()
    return HttpResponse('Ok')


@load_prevars
def change_name(prevars):
    name_len = 256
    name = prevars.request.POST.get('name')
    if isinstance(name, str) and len(name) > name_len:
        return HttpResponseBadRequest()
    prevars.settings.name = name
    return HttpResponse('Ok')


def get_game_task_generator(difficulty, prevars, trial=None, pair_id=None):
    if difficulty == GameTypes.random:
        return RandomGameTaskGenerator(prevars.zim_file, prevars.graph)
    elif difficulty == GameTypes.trial:
        return TrialGameTaskGenerator(trial)
    else:
        return DifficultGameTaskGenerator(difficulty)


@load_prevars
def get_start(prevars):
    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            prevars.settings.difficulty,
            prevars,
        ),
        prevars.zim_file,
        prevars.graph,
        prevars.settings,
    )
    return prevars.redirect_to_curr_page()


@load_prevars
def custom_game_start(prevars, trial_id):
    prevars.settings.difficulty = GameTypes.trial
    t = get_object_or_404(Trial.objects.all(), trial_id=trial_id)
    prevars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes.trial,
            prevars,
            trial=t,
        ),
        prevars.zim_file,
        prevars.graph,
        prevars.settings,
    )
    return prevars.redirect_to_curr_page()


@load_prevars
def get_random_start(prevars):
    prevars.game_operator = GameOperator.create_game(
        RandomGameTaskGenerator(prevars.zim_file, prevars.graph),
        prevars.zim_file,
        prevars.graph,
        prevars.settings,
    )
    return prevars.redirect_to_curr_page()


@requires_game
def get_continue(prevars):
    return prevars.redirect_to_curr_page()


@requires_game
def get_back(prevars):
    prevars.game_operator.jump_back()
    return prevars.redirect_to_curr_page()


@requires_game
def get_hint_page(prevars):
    article = prevars.game_operator.last_page

    template = loader.get_template('wiki/hint_page.html')
    context = {
        'content': article.content.decode(),
    }
    return HttpResponse(template.render(context, prevars.request))


@requires_finished_game
def show_path_page(prevars):
    page_id = prevars.game_operator.start_page_id
    start = prevars.zim_file[page_id].title
    our_path = [
        prevars.zim_file[idx].title for idx in prevars.game_operator.path
    ]
    if len(our_path) == 0:
        our_path = ['Мы не хотим лишать вас удовольствия искать путь самостоятельно']
    user_path = [start]

    game_id = prevars.game_operator.game_id
    turns = Turn.objects.filter(game_id=game_id).order_by('step')

    user_path += [prevars.zim_file[turn.to_page_id].title for turn in turns]
    context = {
        'our_from': our_path[0],
        'user_from': user_path[0],
        'our_path': our_path[1:],
        'user_path': user_path[1:],
    }
    template = loader.get_template('wiki/show_path_page.html')
    return HttpResponse(template.render(context, prevars.request))


def get_end_page(prevars):
    surrendered = prevars.game_operator.surrendered
    prevars.game_operator.game.save()
    context = {
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'pair_id': prevars.game_operator.game_pair.pair_id,
        'move_end': inflection.mupltiple_suffix(
            prevars.game_operator.game.steps
        ),
        'name': prevars.settings.name,
        'game_id': prevars.game_operator.game_id,
        'host': prevars.request.META.get('HTTP_HOST', 'localhost'),
        'key': prevars.game_operator.game.multiplayer.multiplayer_key,
        'title_text': 'Победа' if not surrendered else 'Игра окончена',
        'results_table': get_results(
            prevars.game_operator.game.multiplayer,
            prevars.settings.user_id
        )
    }
    template = loader.get_template('wiki/end_page.html')
    return HttpResponse(template.render(context, prevars.request))


@requires_game
def surrender(prevars):
    prevars.game_operator.surrender()
    return get_end_page(prevars)


def get_login_page(request):
    redirect_uri = 'https://wikirace.lksh.ru/' + settings.ROOT_PATH + "login"
    context = {
        'client_id': settings.VK_CLIENT_ID,
        'redirect_uri': redirect_uri
    }
    template = loader.get_template('wiki/login_page.html')
    if len(request.GET) == 0:
        return HttpResponse(template.render(context, request))

    if request.GET.get('code', None) is None:
        return HttpResponse(template.render(context, request))

    code = request.GET['code']
    href = 'https://oauth.vk.com/access_token?' + \
           'client_id={id}&client_secret={secret}' + \
           '&redirect_uri={link}' + \
           '&code={code}'
    href = href.format(id=settings.VK_CLIENT_ID,
                       secret=settings.VK_SECRET_KEY,
                       link=redirect_uri,
                       code=code)
    r = requests.get(href)
    r = r.json()
    token = r.get('access_token', None)
    user_id = r.get('user_id', None)
    if token is None or user_id is None:
        return HttpResponse(template.render(context, request))
    vk_id = str(user_id)
    user = UserSettings.objects.filter(vk_id=vk_id)
    if user.exists():
        user = user[0]
        request.session['user_id'] = user.user_id
        user.access_token = token
        user.save()
        return redirect_to('/')

    href_get_user = 'https://api.vk.com/method/users.get?' + \
                    'user_ids={id}&' + \
                    'access_token={token}&' + \
                    'v=5.103'
    href_get_user = href_get_user.format(id=vk_id, token=token)

    r = requests.get(href_get_user)
    r = r.json()
    error = r.get('error', None)
    if error is not None:
        return HttpResponse(template.render(context, request))

    r = r['response'][0]
    name = r["first_name"] + " " + r["last_name"]

    user = UserSettings.objects.create(vk_id=vk_id, vk_access_token=token)
    user.name = name
    user.save()
    request.session['user_id'] = user.user_id

    return redirect_to("/")


@load_prevars
def get_global_rating_page(prevars):
    users_table = [
        {
            'is_current_user': (user.user_id == prevars.settings.user_id),
            'name': user.name,
            'rate': user.rate
        }
        for user in UserSettings.objects.filter(~Q(vk_id="")).order_by('-rate')[:settings.RATING_TOP_N]
    ]
    current_user_above = len(list(filter(lambda x: x['is_current_user'], users_table))) == 0
    current_user_vkid = prevars.settings.vk_id
    current_user_name = prevars.settings.name
    current_user_rate = prevars.settings.rate
    current_user_place = UserSettings.objects.filter(~Q(vk_id=""), ~Q(
        vk_id=current_user_vkid), rate__gt=current_user_rate).count() + 1
    context = {
        'results_table': {
            'global_table': users_table,
            'user': {
                'above': current_user_above,
                'place': current_user_place,
                'name': current_user_name,
                'rate': current_user_rate,
            }
        }
    }
    template = loader.get_template('wiki/rating_page.html')
    return HttpResponse(template.render(context, prevars.request))


@requires_finished_game
def end_page(prevars):
    return get_end_page(prevars)


def change_stats(prevars: PreVariables):
    game_type = prevars.settings.difficulty
    trial_id = None
    if game_type == GameTypes.trial:
        game_pair_id = prevars.game_operator.game_pair
        trial_id = Trial.objects.filter(game_pair=game_pair_id)[0]
    user_id = prevars.settings
    hops = prevars.game_operator.game.steps
    time = timezone.now() - prevars.game_operator.game.start_time
    stat = GameStats.objects.create(
        class_type=game_type,
        trial_id=trial_id,
        user_id=user_id,
        hops=hops,
        time=time,
        game_pair=prevars.game_operator.game_pair
    )
    stat.save()
    user_id.rate += user_rating.calculate_rate_change(stat)
    user_id.save()


@requires_game
def get(prevars, title_name):
    article = prevars.zim_file[title_name].follow_redirect()
    if article.is_empty or article.is_redirecting:
        return HttpResponseNotFound()

    if article.namespace != ZIMFile.NAMESPACE_ARTICLE:
        return HttpResponse(article.content, content_type=article.mimetype)

    if not prevars.game_operator.is_jump_allowed(article):
        return prevars.redirect_to_curr_page()
    prevars.game_operator.jump_to(article)

    if prevars.game_operator.finished:
        change_stats(prevars)
        return get_end_page(prevars)

    template = loader.get_template('wiki/game_page.html')
    context = {
        'title': article.title,
        'from': prevars.game_operator.first_page.title,
        'to': prevars.game_operator.last_page.title,
        'counter': prevars.game_operator.game.steps,
        'pair_id': prevars.game_operator.game_pair.pair_id,
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
        return redirect_to('/')
    else:
        form = FeedbackForm()

    context = {
        'form': form,
    }
    template = loader.get_template('wiki/feedback_page.html')
    return HttpResponse(template.render(context, prevars.request))


@load_prevars
def join_game_by_key(prevars, multiplayer_key):
    multiplayer = get_object_or_404(
        MultiplayerPair, multiplayer_key=multiplayer_key)
    prevars.game_operator = GameOperator.create_game(
        MultipayerGameTaskGenerator(multiplayer),
        prevars.zim_file,
        prevars.graph,
        prevars.settings,
    )
    return prevars.redirect_to_curr_page()


@load_prevars
def show_results_table(prevars, multiplayer_key):
    multiplayer = get_object_or_404(
        MultiplayerPair, multiplayer_key=multiplayer_key)

    template = loader.get_template('wiki/leaderboard_page.html')
    context = {
        'results_table': get_results(
            multiplayer,
            prevars.settings.user_id
        ),
        'only_global': False
    }
    return HttpResponse(
        template.render(context, prevars.request),
        content_type='text/html'
    )


def get_results(multiplayer, user_id):
    private_table = results_table(
        multiplayer,
        user_id
    )
    global_table = results_table(
        multiplayer.game_pair,
        user_id
    )
    return {
        'private_table': private_table,
        'global_table': global_table,
    }


def results_table(game_holder, user_id, top_n=-1):
    if isinstance(game_holder, MultiplayerPair):
        games = list(Game.objects.filter(multiplayer_id=game_holder.multiplayer_id,
                                         current_page_id=game_holder.game_pair.end_page_id).all())
    else:
        games = list(Game.objects.filter(multiplayer__game_pair_id=game_holder.pair_id,
                                         current_page_id=game_holder.end_page_id).all())

    games.sort(key=lambda x: x.steps)

    results_table = []
    used_ids = set()
    for game in games:
        if game.user_settings is None:
            continue

        if len(used_ids) == top_n:
            break

        curr_game_user_id = game.user_settings.user_id
        if curr_game_user_id in used_ids:
            continue
        used_ids.add(curr_game_user_id)

        name = game.user_settings.name

        results_table.append({
            'name': name,
            'steps': game.steps,
            'is_me': user_id == curr_game_user_id
        })
    return results_table


@load_prevars
def show_trial_results_table(prevars, trial_id):
    trial = get_object_or_404(Trial, trial_id=trial_id)
    results = results_table(trial.game_pair, prevars.settings.user_id)
    context = {
        'results_table': {
            'global_table': results
        },
        'only_global': True
    }

    template = loader.get_template('wiki/leaderboard_page.html')
    return HttpResponse(
        template.render(context, prevars.request),
        content_type='text/html'
    )
