from django.http import HttpResponse
from django.conf import settings
from wiki.GameOperator import GameOperator
import requests
from wiki.ZIMFile import MyZIMFile
from wiki.GraphReader import GraphReader


def get(request, title_name):
	print("req") #delete
	zim = MyZIMFile('F:\\LKSH\\New\\by_category\\wikipedia_ru_geography_nopic_2019-05.zim')
	graph = GraphReader('F:\\LKSH\\offset0', 'F:\\LKSH\\edges0')  # later
	if request.session.get('steps', None) is None:
		request.session['steps'] = 0
		
		request.session['operator'] = GameOperator(zim, graph)
		# request.session['operator'].current_page_id - start
		# request.session['operator'].end_page_id - finish
			
		return HttpResponse('New game!')
	
	# nextPage(title_name) - True - конец игры False - нет None - не статья
	requested_page = zim.get_by_url(title_name)
	
	if (requested_page.namespace == "A"):
		request.session['steps'] += 1
		result = request.session['operator'].next_page(title_name)
		if result == True:
			return HttpResponse('You win!')
		elif result is None:
			return HttpResponse('Error! Not article!')
		# wiki_page_request = requests.get(settings.WIKI_MIRROR_HOST + title_name)  # здесь вместо title_name current_page_id
		wiki_page = zim._get_article_by_index(request.session['operator'].current_page_id).data.decode('utf-8')
		# mimetype - тип. У статьи - text/html
		return HttpResponse(wiki_page.data, wiki_page.mimetype)
	
	return HttpResponse(requested_page.data, requested_page.mimetype)
	
