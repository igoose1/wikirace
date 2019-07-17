from django.contrib import admin
from wiki.models import Game, Feedback, Turn, GamePair


class GameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'game_pair', 'steps', 'finished', 'start_time', 'last_action_time']
    ordering = ['game_id']


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'time']
    ordering = ['time']


class TurnAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'game_pair', 'time']
    ordering = ['time']


class GamePairAdmin(admin.ModelAdmin):
    list_display = ['pair_id', 'start_page_id', 'end_page_id']
    ordering = ['pair_id']


admin.site.register(Game, GameAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Turn, TurnAdmin)
admin.site.register(GamePair, GamePairAdmin)
