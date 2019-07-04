from django.http import HttpResponse
from django.conf import settings
from wiki.GameOperator import GameOperator
from wiki.models import Game
from var_init import *


def get(request, title_name):
    currOperator = GameOperator(zim, graph)
    if request.session.get('operator', None) is None or input('TYPE') == 's':
        # начало игры
        currOperator.initialize_game()
        Game.objects.create(session_id=request.session.session_key,
                            first=currOperator.current_page_id,
                            last=currOperator.end_page_id,
                            steps=0,
							ended=False)	
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
        curr_game = Game.objects.filter(session_id=request.session.session_key)[0]
        curr_game.steps = request.session['steps']
        curr_game.ended = result
        curr_game.commit()
        if result == True:
            return HttpResponse('You win!')
        elif result is None:
            return HttpResponse('Error! Not article!')
        wiki_page = zim._get_article_by_index(currOperator.current_page_id)
        # mimetype - тип. У статьи - text/html
        return HttpResponse(wiki_page.data, wiki_page.mimetype)

    return HttpResponse(requested_page.data, requested_page.mimetype)
