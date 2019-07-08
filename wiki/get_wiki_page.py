from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.conf import settings
from django.template import loader
from django.utils import timezone

from .GameOperator import GameOperator
from .GraphReader import GraphReader
from .ZIMFile import MyZIMFile
from .form import FeedbackForm


def answer(func, requires_game=False,
          load_game_operator=False, save_game_operator=False):
    class PreVariables:
        def __init__(self, request):
            self.zim_file = MyZIMFile(settings.WIKI_ZIMFILE_PATH)
            self.graph = GraphReader(
                settings.GRAPH_OFFSET_PATH,
                settings.GRAPH_EDGES_PATH
            )
            self.game_operator = GameOperator(zim_file, graph)
            self.request = request

    def wrapper(request, *args, **kwargs):
        prevars = PreVariables(request)
        session_operator = request.session.get('operator', None)
        if requires_game and session_operator is None:
            return HttpResponseRedirect('/')
        if load_game_operator:
            prevars.game_operator.load(session_operator)

        res = func(prevars, *args, **kwargs)
        if save_game_operator:
            request.session['operator'] = prevars.game_operator.save()
        return res

    return wrapper


@answer(requires_game=True, load_game_operator=True, save_game_operator=True)
def get(prevars, title_name):
    content = prevars.zim_file.get_by_url('/' + title_name)
    if content is None:
        raise Http404()

    data, namespace, mime_type = content
    if namespace != 'A':
        return HttpResponse(data, content_type=mime_type)

    prevars.game_operator.load_testing = (
        "loadtesting" in prevars.request.GET
        and prevars.request.META["REMOTE_ADDR"].startswith("127.0.0.1")
    )

    next_page_result = prevars.game_operator.next_page('/' + title_name)

    if next_page_result: # TODO
        return winpage(prevars.request) # TODO
    elif next_page_result is None: # TODO
        return HttpResponseRedirect(
            zim_file.read_directory_entry_by_index(prevars.game_operator.current_page_id)['url']
        ) # TODO

    template = loader.get_template('wiki/page.html')
    context = {
        'title': zim_file.read_directory_entry_by_index(prevars.game_operator.current_page_id)['title'], # TODO
        'from': zim_file.read_directory_entry_by_index(prevars.game_operator.start_page_id)['title'], # TODO
        'to': zim_file.read_directory_entry_by_index(prevars.game_operator.end_page_id)['title'], # TODO
        'counter': prevars.game_operator.steps,
        'wiki_content': zim_file.get_by_index(prevars.game_operator.current_page_id).data.decode('utf-8'), # TODO
        'history_empty': prevars.game_operator.is_history_empty()
    }
    return HttpResponse(template.render(context, prevars.request), content_type=mime_type)


@answer(save_game_operator=True)
def get_start(prevars):
    difficulty = get_settings(prevars.request)['difficulty']
    prevars.game_operator.initialize_game(difficulty)
    return HttpResponseRedirect(
        prevars.zim_file.read_directory_entry_by_index(prevars.game_operator.current_page_id)['url']
    )


@answer(requires_game=True, load_game_operator=True, save_game_operator=True)
def get_back(prevars):
    prevars.game_operator.prev_page()
    return HttpResponseRedirect(
        prevars.zim_file.read_directory_entry_by_index(prevars.game_operator.current_page_id)['url']
    )


@answer(requires_game=True, load_game_operator=True)
def get_continue(prevars):
    return HttpResponseRedirect(
        self.zim_file.read_directory_entry_by_index(self.game_operator.current_page_id)['url']
    )


@answer(requires_game=True, load_game_operator=True)
def winpage(prevars):
    ending = ''
    if prevars.game_operator.steps % 10 == 1 and prevars.game_operator.steps % 100 != 11:
        pass
    elif prevars.game_operator.steps % 10 in [2, 3, 4] and prevars.game_operator.steps % 100 not in [12, 13, 14]:
        ending = 'а'
    else:
        ending = 'ов'
    settings_user = get_settings(request)
    context = {
        'from': prevars.zim_file.read_directory_entry_by_index(prevars.game_operator.start_page_id)['title'], # TODO
        'to': prevars.zim_file.read_directory_entry_by_index(prevars.game_operator.end_page_id)['title'], # TODO
        'counter': prevars.game_operator.steps,
        'move_end': ending,
        'name': settings_user['name']
    }
    template = loader.get_template('wiki/win_page.html')
    prevars.request.session['operator'] = None
    return HttpResponse(
        template.render(context, prevars.request),
    )


@answer
def get_main_page(prevars):
    template = loader.get_template('wiki/start_page.html')
    session_operator = prevars.request.session.get('operator', None)
    is_playing = False
    if session_operator and not session_operator[2]:
        is_playing = True

    context = {
        'is_playing': is_playing,
        'settings': get_settings(prevars.request)
    }
    return HttpResponse(template.render(context, prevars.request))


@answer(requires_game=True, load_game_operator=True)
def get_hint_page(request):
    content = prevars.zim_file.get_by_index(game_operator.end_page_id)
    data, namespace, mime_type = content

    context = {
        'content': data.decode('utf-8'),
    }

    template = loader.get_template('wiki/hint_page.html')
    return HttpResponse(template.render(context, prevars.request))


@answer
def get_feedback_page(prevars):
    if prevars.request.method == "POST":
        form = FeedbackForm(prevars.request.POST)
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
    return HttpResponse(template.render(context=context, request=prevars.request))


@answer
def change_settings(prevars):
    val = prevars.request.POST.get('difficulty', None)
    name = prevars.request.POST.get('name', 'no name')
    diff_id = get_difficulty_level_by_name(val)
    if diff_id is None or len(name) > 16:
        return HttpResponseServerError()
    prevars.request.session['settings'] = {'difficulty': diff_id, 'name': name}
    return HttpResponse('Ok')


 # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO
 # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO
 # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO


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


def get_settings(request):
    default = {'difficulty': -1, 'name': 'no name'}
    settings_user = request.session.get('settings', default)
    for key in default.keys():
        if key not in settings_user.keys():
            settings_user[key] = default[key]
    return settings_user
