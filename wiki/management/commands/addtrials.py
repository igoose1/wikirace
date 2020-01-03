from django.core.management.base import BaseCommand
from contextlib import closing
from wiki.models import GamePair, Trial, TrialType
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
                game_pair = GamePair.get_or_create(start.index, end.index)

                begin = trial.get('begin', None)
                if begin is not None:
                    begin = datetime.datetime.strptime(begin, "%d/%m/%Y")
                else:
                    begin = datetime.datetime.now()

                duration_in_hours = int(trial.get('length', "0"))

                diff = trial.get('difficulty', 0)
                hops = trial.get('min_hops', 4)
                trial_type = TrialType.EVENT
                if duration_in_hours == 0:
                    trial_type = TrialType.TRIAL

                Trial.objects.get_or_create(
                    trial_name=trial['name'],
                    game_pair=game_pair,
                    _begin=begin,
                    _length=datetime.timedelta(hours=int(duration_in_hours)),
                    type=trial_type,
                    difficulty=diff,
                    min_hops=hops
                )

                print("Trial {name} added".format(name=trial['name']))
