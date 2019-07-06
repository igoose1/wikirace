from django.contrib import admin
from wiki.models import GameStat, Feedback


class GameStatAdmin(admin.ModelAdmin):
	list_display = ['game_id', 'start_page_id', 'end_page_id',
					'steps', 'finished', 'start_time', 'last_action_time']
	ordering = ['game_id']


class FeedbackAdmin(admin.ModelAdmin):
	list_display = ['text', 'time']
	ordering = ['time']


admin.site.register(GameStat, GameStatAdmin)
admin.site.register(Feedback, FeedbackAdmin)
