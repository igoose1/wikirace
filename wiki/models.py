from django.db import models
from django.conf import settings
from random import randrange
from django.utils import timezone
import hashlib
from datetime import timedelta
from enum import Enum


class GameTypes(Enum):
    random = "random"
    easy = "easy"
    medium = "medium"
    hard = "hard"
    trial = "trial"
    by_id = "by_id"


class UserSettings(models.Model):
    user_id = models.AutoField(primary_key=True)
    vk_id = models.CharField(
        max_length=256,
        null=False
    )
    rate = models.FloatField(default=0)
    vk_access_token = models.CharField(
        max_length=256,
        null=False
    )
    _difficulty = models.CharField(
        max_length=10,
        default=GameTypes.easy.value,
    )
    _name = models.CharField(max_length=256, null=True)

    @property
    def name(self):
        return self._name if self._name else 'Player #{id}'.format(id=self.user_id)

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def difficulty(self):
        return GameTypes(self._difficulty)

    @difficulty.setter
    def difficulty(self, value):
        self._difficulty = value.value

    def dict(self):
        return {
            'difficulty': self.difficulty,
            'name': self.name,
            'name_init_needed': (self._name is None),
        }

    def __str__(self):
        return 'id:{id}; name:{name}; diff:{diff};'.format(
            id=self.user_id,
            diff=self.difficulty,
            name=self.name,
        )


class GamePair(models.Model):
    """
    Ids of all pairs. Uniquely representable structure of game.
    """
    pair_id = models.AutoField(primary_key=True)
    start_page_id = models.IntegerField(default=0)
    end_page_id = models.IntegerField(default=0)
    possible_path = models.TextField(default="", null=True, blank=True)

    class Meta:
        unique_together = (('start_page_id', 'end_page_id'),)

    def __str__(self):
        return '{id}: {start} -> {end}'.format(
            id=self.pair_id,
            start=self.start_page_id,
            end=self.end_page_id
        )

    @staticmethod
    def get_or_create(start_page_id, end_page_id, possible_path=''):
        return GamePair.objects.get_or_create(
            start_page_id=start_page_id,
            end_page_id=end_page_id,
            defaults={'possible_path': possible_path},
        )[0]

    @staticmethod
    def get_or_create_by_path(path):
        return GamePair.get_or_create(
            start_page_id=path[0],
            end_page_id=path[-1],
            possible_path=' '.join(map(str, path)),
        )


class MultiplayerPairManager(models.Manager):
    def create(self, *args, **kwargs):
        kwargs['multiplayer_key'] = self._generate_multiplayer_key()
        return super(MultiplayerPairManager, self).create(*args, **kwargs)

    def _generate_multiplayer_key(self):
        suffix = settings.SECRET_KEY
        counter = 0
        multiplayer_key = None
        while multiplayer_key is None or MultiplayerPair.objects.filter(multiplayer_key=multiplayer_key).count() > 0:
            counter += 1
            suffix += 'a'
            hashed_string = hashlib.sha256(
                (str(randrange(0, 1000000000)) + suffix).encode()
            ).hexdigest()
            multiplayer_key = hashed_string[:min(6 + counter // 32, 16)]
        return multiplayer_key


class MultiplayerPair(models.Model):
    objects = MultiplayerPairManager()

    multiplayer_id = models.AutoField(primary_key=True)
    game_pair = models.ForeignKey(GamePair, models.CASCADE, null=False)
    multiplayer_key = models.CharField(default='', max_length=64, blank=True)

    class Meta:
        unique_together = (('multiplayer_key',),)

    @property
    def from_page_id(self):
        return self.game_pair.start_page_id

    @property
    def to_page_id(self):
        return self.game_pair.end_page_id


class Game(models.Model):
    user_settings = models.ForeignKey(UserSettings, null=True,
                                      on_delete=models.SET_NULL)
    multiplayer = models.ForeignKey(MultiplayerPair, null=False,
                                    on_delete=models.CASCADE)
    game_id = models.AutoField(primary_key=True)
    current_page_id = models.IntegerField(null=True, default=None)
    start_time = models.DateTimeField(null=True)
    last_action_time = models.DateTimeField()
    surrendered = models.BooleanField(default=False)

    @property
    def steps(self):
        return Turn.objects.filter(game_id=self.game_id).count()

    @property
    def game_pair(self):
        return self.multiplayer.game_pair

    @property
    def start_page_id(self):
        return self.game_pair.start_page_id

    @property
    def end_page_id(self):
        return self.game_pair.end_page_id

    @property
    def possible_path(self):
        return self.multiplayer.game_pair.possible_path

    @property
    def finished(self):
        return self.current_page_id == self.end_page_id

    def __str__(self):
        return '{id}: {sp} -> {ep} ({la})'.format(
            id=self.game_id,
            sp=self.game_pair.start_page_id,
            ep=self.game_pair.end_page_id,
            la=self.last_action_time
        )


class Feedback(models.Model):
    """
    Model containing data of feedback
    """

    name = models.CharField(default='Анонимно', max_length=30)
    text = models.TextField(null=True, max_length=1000)
    time = models.DateTimeField(null=True)

    def __str__(self):
        return '{name} at {time}'.format(
            name=self.name,
            time=self.time
        )


class TurnType(Enum):
    FWD = 'forward'
    BWD = 'backward'


class Turn(models.Model):
    """
    Saving of user's steps
    """
    game_id = models.IntegerField()
    time = models.DateTimeField()
    from_page_id = models.IntegerField()
    to_page_id = models.IntegerField()
    turn_id = models.AutoField(primary_key=True)
    step = models.IntegerField(default=0)
    turn_type = models.CharField(
        max_length=16,
        choices=[(tag, tag.value) for tag in TurnType],
        default=TurnType.FWD
    )

    def __str__(self):
        return '{id}: {fp} -> {tp}'.format(
            id=self.turn_id,
            fp=self.from_page_id,
            tp=self.to_page_id,
        )


class TrialType(Enum):
    TRIAL = "Trial"
    EVENT = "Event"


class Trial(models.Model):
    min_hops = models.IntegerField(default=4)
    trial_id = models.AutoField(primary_key=True)
    trial_name = models.CharField(default='испытание', max_length=200)
    game_pair = models.ForeignKey(GamePair, models.CASCADE, null=False)
    _length = models.DurationField(default=timedelta(seconds=0))
    _begin = models.DateTimeField()
    type = models.CharField(
        max_length=16,
        choices=[(str(tag), tag.value) for tag in TrialType],
        default=TrialType.TRIAL
    )
    difficulty = models.FloatField(default=0)

    @property
    def is_event_active(self):
        return (timezone.now() < (self._begin + self._length)) and (timezone.now() > self._begin)

    @property
    def time_left(self):
        return self._begin + self._length - timezone.now()

    @property
    def hours_left(self):
        return int(self.time_left.total_seconds() // 3600)

    def __str__(self):
        return '{trial_name}, ind = {trial_id}, path: {from_page_id} -> {to_page_id}'.format(
            trial_name=self.trial_name,
            trial_id=self.trial_id,
            from_page_id=self.game_pair.start_page_id,
            to_page_id=self.game_pair.end_page_id
        )


class GameStats(models.Model):
    class_type = models.CharField(
        max_length=64,
        choices=[(tag, tag.value) for tag in GameTypes]
    )
    game_pair = models.ForeignKey(GamePair, models.CASCADE, null=False)
    rate_delta = models.FloatField(default=0)
    trial_id = models.ForeignKey(Trial, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(UserSettings, on_delete=models.CASCADE, null=False)
    hops = models.IntegerField(default=0)
    time = models.DurationField()

    @staticmethod
    def get_average_hops_count():
        val = GameStats.objects.aggregate(models.Avg('hops'))
        return val.get('hops__avg', None)

    @staticmethod
    def get_min_hops_count():
        val = GameStats.objects.aggregate(models.Min('hops'))
        return val.get('hops__min', None)

    @staticmethod
    def get_attemps_count(user, game_pair):
        val = GameStats.objects.filter(user_id=user, game_pair=game_pair).aggregate(models.Count('user_id'))
        return val.get('user_id__count', 1)
