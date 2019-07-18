from django.db import models
import datetime


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
            possible_path=possible_path,
        )[0]

    @staticmethod
    def get_or_create_by_path(path):
        return GamePair.objects.get_or_create(
            start_page_id=path[0],
            end_page_id=path[-1],
            possible_path=' '.join(map(str, path)),
        )[0]


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    game_pair = models.ForeignKey(GamePair, models.CASCADE, null=False)
    current_page_id = models.IntegerField(null=True, default=None)
    steps = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    last_action_time = models.DateTimeField()
    surrendered = models.BooleanField(default=False)

    @property
    def start_page_id(self):
        return self.game_pair.start_page_id

    @property
    def end_page_id(self):
        return self.game_pair.end_page_id

    @property
    def possible_path(self):
        return self.game_pair.possible_path

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


class Turn(models.Model):
    """
    Saving of user's steps
    """
    game_id = models.IntegerField()
    time = models.DateTimeField()
    from_page_id = models.IntegerField()
    to_page_id = models.IntegerField()
    turn_id = models.AutoField(primary_key=True)

    def __str__(self):
        return '{id}: {fp} -> {tp}'.format(
            id=self.turn_id,
            fp=self.from_page_id,
            tp=self.to_page_id,
        )


class Trial(models.Model):
    trial_id = models.AutoField(primary_key=True)
    trial_name = models.CharField(default='испытание', max_length=200)
    game_pair = models.ForeignKey(GamePair, models.CASCADE, null=False)

    def __str__(self):
        return '{trial_name}, ind = {trial_id}, path: {from_page_id} -> {to_page_id}'.format(
            trial_name=self.trial_name,
            trial_id=self.trial_id,
            from_page_id=self.game_pair.start_page_id,
            to_page_id=self.game_pair.end_page_id
        )
