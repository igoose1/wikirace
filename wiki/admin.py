from django.contrib import admin
from wiki.models import Game, Feedback, Turn


class GameStatAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'start_page_id', 'end_page_id',
                    'steps', 'finished', 'start_time', 'last_action_time']
    ordering = ['game_id']


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'time']
    ordering = ['time']


class TurnAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'from_page_id', 'to_page_id', 'time']
    ordering = ['time']


admin.site.register(Game, GameStatAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Turn, TurnAdmin)
