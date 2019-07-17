from django.http import HttpResponse,\
                        HttpResponseBadRequest,\
                        HttpResponseRedirect,\
                        HttpResponseNotFound
from django.conf import settings
from django.template import loader
from django.utils import timezone
from django.shortcuts import get_object_or_404
from . import inflection
from .GameOperator import GameOperator,\
                          RandomGameTaskGenerator,\
                          DifficultGameTaskGenerator,\
                          TrialGameTaskGenerator,\
                          GameTypes
from .GraphReader import GraphReader
from .ZIMFile import ZIMFile
from .form import FeedbackForm
from .models import Turn,\
                    Trial
from wiki.file_holder import file_holder


@file_holder
class PreVariables:
    def __init__(self, request):
        self.zim_file = self._add_file(
            ZIMFile(
                settings.WIKI_ZIMFILE_PATH,
                settings.WIKI_ARTICLES_INDEX_FILE_PATH
            )
        )
        self.graph = self._add_file(
            GraphReader(
                settings.GRAPH_OFFSET_PATH,
                settings.GRAPH_EDGES_PATH
            )
        )
        self.game_operator = GameOperator.deserialize_game_operator(
            request.session.get('operator', None),
            self.zim_file,
            self.graph,
            'loadtesting' in request.GET and request.META['REMOTE_ADDR'].startswith('127.0.0.1')
        )
        self.session_operator = None
        self.request = request


def load_pre_vars(func):
    def wrapper(request, *args, **kwargs):
        pre_vars = PreVariables(request)
        try:
            pre_vars.session_operator = pre_vars.request.session.get('operator', None)
            res = func(pre_vars, *args, **kwargs)
            if pre_vars.game_operator is not None:
                pre_vars.request.session['operator'] = pre_vars.game_operator.serialize_game_operator()
            else:
                pre_vars.request.session['operator'] = None
        finally:
            pre_vars.close()
        return res

    return wrapper


def requires_game(func):
    def wrapper(pre_vars, *args, **kwargs):
        if pre_vars.session_operator is None:
            return HttpResponseRedirect('/')
        return func(pre_vars, *args, **kwargs)

    return load_pre_vars(wrapper)


def get_settings(settings_user):
    default = {'difficulty': GameTypes.random.value, 'name': 'no name'}
    for key in default.keys():
        settings_user[key] = settings_user.get(key, default[key])
    return settings_user


@load_pre_vars
def get_main_page(pre_vars):
    template = loader.get_template('wiki/start_page.html')
    trial_list = Trial.objects.all()
    context = {
        'is_playing': pre_vars.session_operator is not None and not pre_vars.game_operator.finished,
        'settings': get_settings(
            pre_vars.request.session.get('settings', dict())
        ),
        'trial_list': trial_list,
    }
    return HttpResponse(template.render(context, pre_vars.request))


@load_pre_vars
def change_settings(pre_vars):
    name_len = 16

    difficulty = pre_vars.request.POST.get('difficulty', None)
    name = pre_vars.request.POST.get('name')

    if difficulty not in [el.value for el in GameTypes] or (isinstance(name, str) and len(name) > name_len):
        return HttpResponseBadRequest()

    pre_vars.request.session['settings'] = {
        'difficulty': GameTypes(difficulty).value,
        'name': name
    }
    return HttpResponse('Ok')


def get_game_task_generator(difficulty, pre_vars, trial=None):
    if difficulty == GameTypes.random:
        return RandomGameTaskGenerator(pre_vars.zim_file, pre_vars.graph)
    elif difficulty == GameTypes.trial:
        return TrialGameTaskGenerator(trial)
    else:
        return DifficultGameTaskGenerator(difficulty)


@load_pre_vars
def get_start(pre_vars):
    user_settings = get_settings(
        pre_vars.request.session.get('settings', dict())
    )

    if user_settings.get('difficulty', None) is None:
        return HttpResponseRedirect('/')

    if isinstance(user_settings['difficulty'], int):
        pre_vars.request.session['settings'] = get_settings(dict())
        return HttpResponseBadRequest()

    pre_vars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes(
                user_settings['difficulty']
            ),
            pre_vars,
        ),
        pre_vars.zim_file,
        pre_vars.graph
    )
    return HttpResponseRedirect(pre_vars.game_operator.current_page.url)


@load_pre_vars
def custom_game_start(pre_vars, trial_id):
    t = get_object_or_404(Trial.objects.all(), trial_id=trial_id)
    pre_vars.game_operator = GameOperator.create_game(
        get_game_task_generator(
            GameTypes.trial,
            pre_vars,
            trial=t,
        ),
        pre_vars.zim_file,
        pre_vars.graph
    )
    return HttpResponseRedirect('/' + pre_vars.game_operator.current_page.url)


@load_pre_vars
def get_random_start(pre_vars):
    pre_vars.game_operator = GameOperator.create_game(
        RandomGameTaskGenerator(pre_vars.zim_file, pre_vars.graph),
        pre_vars.zim_file,
        pre_vars.graph
    )
    return HttpResponseRedirect(pre_vars.game_operator.current_page.url)


@requires_game
def get_continue(pre_vars):
    return HttpResponseRedirect(pre_vars.game_operator.current_page.url)


@requires_game
def get_back(pre_vars):
    pre_vars.game_operator.jump_back()
    return HttpResponseRedirect(pre_vars.game_operator.current_page.url)


@requires_game
def get_hint_page(pre_vars):
    article = pre_vars.game_operator.last_page

    template = loader.get_template('wiki/hint_page.html')
    context = {
        'content': article.content.decode(),
    }
    return HttpResponse(template.render(context, pre_vars.request))


@requires_game
def show_path_page(pre_vars):
    page_id = pre_vars.game_operator.game.start_page_id
    start = pre_vars.zim_file[page_id].title
    our_path = [
        pre_vars.zim_file[idx].title for idx in pre_vars.game_operator.path
    ]
    if len(our_path) == 0:
        our_path = [start]
    user_path = [start]
    game_id = pre_vars.game_operator.game.game_id
    turns = Turn.objects.filter(game_id=game_id).order_by('time')

    user_path += [pre_vars.zim_file[turn.to_page_id].title for turn in turns]
    context = {
        'from': our_path[0],
        'our_path': our_path[1:],
        'user_path': user_path[1:],
    }
    template = loader.get_template('wiki/show_path_page.html')
    return HttpResponse(template.render(context, pre_vars.request))


def get_end_page(pre_vars):
    settings_user = get_settings(
        pre_vars.request.session.get('settings', dict())
    )
    surrendered = pre_vars.game_operator.surrendered
    context = {
        'from': pre_vars.game_operator.first_page.title,
        'to': pre_vars.game_operator.last_page.title,
        'counter': pre_vars.game_operator.game.steps,
        'move_end': inflection.multiple_suffix(
            pre_vars.game_operator.game.steps
        ),
        'name': settings_user['name'],
        'game_id': pre_vars.game_operator.game.game_id,
        'title_text': 'Победа' if not surrendered else 'Игра окончена'
    }
    template = loader.get_template('wiki/end_page.html')
    return HttpResponse(template.render(context, pre_vars.request))


@requires_game
def surrender(pre_vars):
    pre_vars.game_operator.surrender()
    return get_end_page(pre_vars)


@requires_game
def get(pre_vars, title_name):
    article = pre_vars.zim_file[title_name].follow_redirect()
    if article.is_empty or article.is_redirecting:
        return HttpResponseNotFound()

    if article.namespace != ZIMFile.NAMESPACE_ARTICLE:
        return HttpResponse(article.content, content_type=article.mimetype)

    if not pre_vars.game_operator.is_jump_allowed(article):
        return HttpResponseRedirect(
            pre_vars.game_operator.current_page.url
        )

    pre_vars.game_operator.jump_to(article)

    if pre_vars.game_operator.finished:
        return get_end_page(pre_vars)

    template = loader.get_template('wiki/game_page.html')
    context = {
        'title': article.title,
        'from': pre_vars.game_operator.first_page.title,
        'to': pre_vars.game_operator.last_page.title,
        'counter': pre_vars.game_operator.game.steps,
        'wiki_content': article.content.decode(),
        'history_empty': pre_vars.game_operator.is_history_empty
    }
    return HttpResponse(
        template.render(context, pre_vars.request),
        content_type=article.mimetype
    )


@load_pre_vars
def choose_custom_game(pre_vars):
    trials = Trial.objects.all()
    template = loader.get_template('wiki/choose_custom_game.html')
    context = {
        'title': 'Выбери челлендж',
        'trials': trials
    }
    return HttpResponse(template.render(context, pre_vars.request))


@load_pre_vars
def get_feedback_page(pre_vars):
    if pre_vars.request.method == 'POST':
        form = FeedbackForm(pre_vars.request.POST).save()
        form.time = timezone.now()
        form.save()
        return HttpResponseRedirect('/')
    else:
        form = FeedbackForm()

    context = {
        'form': form,
    }
    template = loader.get_template('wiki/feedback_page.html')
    return HttpResponse(template.render(context, pre_vars.request))
