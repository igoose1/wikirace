from django.core.management.base import BaseCommand
from contextlib import closing
from wiki.models import GamePair, Trial
from django.conf import settings
import wiki.ZIMFile
import json
import datetime


class Command(BaseCommand):
    help = 'Add trials from file. You should write full path'

    def add_arguments(self, parser):
        parser.add_argument('path_to_file', type=str)

    def handle(self, *args, **options):
        with closing(wiki.ZIMFile.ZIMFile(
            settings.WIKI_ZIMFILE_PATH,
            settings.WIKI_ARTICLES_INDEX_FILE_PATH)
        ) as zim, open(options['path_to_file'], 'r', encoding='utf-8') as file:
            trials = json.loads(file.read())
            for trial in trials:
                start = zim[trial['start']].follow_redirect()
                end = zim[trial['end']].follow_redirect()

                begin = trial.get('begin', None) 
                length = trial.get('length', None)  #hours

                game_pair = GamePair.get_or_create(start.index, end.index)

                if (begin is None or length is None):
                    Trial.objects.get_or_create(
                        trial_name=trial['name'],
                        game_pair=game_pair
                    )
                else:
                    Trial.objects.get_or_create(
                        trial_name=trial['name'],
                        game_pair=game_pair,
                        _begin=datetime.datetime.strptime(begin, "%d/%m/%Y"),
                        _length=datetime.timedelta(hours=int(length))
                    )

                print(("Trial {name} added").format(name=trial['name']))

