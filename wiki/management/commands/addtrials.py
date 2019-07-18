from django.core.management.base import BaseCommand
from wiki.models import GamePair, Trial
from django.conf import settings
import wiki.ZIMFile
import json


class Command(BaseCommand):
    help = 'Add trials from file. You should write full path'

    def add_arguments(self, parser):
        parser.add_argument('path_to_file', type=str)

    def handle(self, *args, **options):
        zim = wiki.ZIMFile.ZIMFile(
            settings.WIKI_ZIMFILE_PATH,
            settings.WIKI_ARTICLES_INDEX_FILE_PATH
        )
        file = open(options['path_to_file'], 'r')
        trials = json.loads(file.read())
        for trial in trials:
            name = trial['name']
            start_page_id = zim[trial['start']].index
            end_page_id = zim[trial['end']].index
            game_pair = GamePair.get_or_create(start_page_id, end_page_id)
            Trial.objects.get_or_create(
                trial_name=name,
                game_pair=game_pair
            )
        file.close()
