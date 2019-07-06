from django.contrib import admin
from wiki.models import GameStat

    
class GameStatAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'start_page_id', 'end_page_id', 
                    'steps', 'finished', 'start_time', 'last_action_time']
    ordering = ['game_id']
    

admin.site.register(GameStat, GameStatAdmin)
