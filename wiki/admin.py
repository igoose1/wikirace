from django.contrib import admin
from wiki.models import Game, Feedback, Turn, Trial, GamePair, MultiplayerPair, UserSettings


class GameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'steps', 'finished', 'start_time', 'last_action_time', 'user_settings', 'got_rate']
    list_display_links = ['user_settings']
    ordering = ['game_id']


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'time']
    ordering = ['time']


class TurnAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'from_page_id', 'to_page_id', 'time']
    ordering = ['time']


class TrialAdmin(admin.ModelAdmin):
    list_display = ['trial_id', 'trial_name', 'game_pair']
    ordering = ['trial_id']


class GamePairAdmin(admin.ModelAdmin):
    list_display = ['pair_id', 'start_page_id', 'end_page_id']
    ordering = ['pair_id']


class MultiplayerAdmin(admin.ModelAdmin):
    list_display = ['multiplayer_id', 'game_pair', 'multiplayer_key']
    ordering = ['multiplayer_id']


class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'name', 'rate', 'vk_id']
    ordering = ['user_id']
    fields = ['_name', 'rate', 'vk_id']
    readonly_fields = ('vk_id',)
    actions = ['nullify_rate']

    def nullify_rate(self, request, queryset):
        queryset.update(rate=0)


admin.site.register(Game, GameAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Turn, TurnAdmin)
admin.site.register(Trial, TrialAdmin)
admin.site.register(GamePair, GamePairAdmin)
admin.site.register(MultiplayerPair, MultiplayerAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
