from django.http import HttpResponse
from django.conf import settings
from wiki.GameOperator import GameOperator
import requests
from wiki.ZIMFile import MyZIMFile
from wiki.GraphReader import GraphReader


def get(request, title_name):
    zim = MyZIMFile('F:\\LKSH\\New\\by_category\\wikipedia_ru_geography_nopic_2019-05.zim')
    graph = GraphReader('F:\\LKSH\\offset0', 'F:\\LKSH\\edges0')  # later
    currOperator = GameOperator(zim, graph)
    if request.session.get('operator', None) is None:  # or input('TYPE') == 's'  # for restart
        # начало игры
        currOperator.initialize_game()
        request.session['steps'] = 0
        request.session['operator'] = currOperator.save()
        print('Start')
    else:
        currOperator.load(request.session['operator'])
    print('From:', zim.read_directory_entry_by_index(currOperator.current_page_id)['title'],
          'To:', zim.read_directory_entry_by_index(currOperator.end_page_id)['title'],
          'Steps:', request.session['steps'])
    # nextPage(title_name) - True - конец игры False - нет None - не статья
    requested_page = zim.get_by_url('/' + title_name)

    if not requested_page:
        wiki_page = zim._get_article_by_index(currOperator.current_page_id)
        return HttpResponse(wiki_page.data, wiki_page.mimetype)
    if (requested_page and requested_page.namespace == "A"):
        request.session['steps'] += 1
        result = currOperator.next_page('/' + title_name)
        request.session['operator'] = currOperator.save()
        if result == True:
            return HttpResponse('You win!')
        elif result is None:
            return HttpResponse('Error! Not article!')
        # wiki_page_request = requests.get(settings.WIKI_MIRROR_HOST + title_name)  # здесь вместо title_name current_page_id
        wiki_page = zim._get_article_by_index(currOperator.current_page_id)
        # mimetype - тип. У статьи - text/html
        return HttpResponse(wiki_page.data, wiki_page.mimetype)

    return HttpResponse(requested_page.data, requested_page.mimetype)
