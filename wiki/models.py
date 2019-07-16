from django.db import models
import datetime


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    start_page_id = models.IntegerField(default=0)
    end_page_id = models.IntegerField(default=0)
    current_page_id = models.IntegerField(null=True, default=None)
    steps = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    last_action_time = models.DateTimeField(default=datetime.datetime.now())
    game_pair = models.ForeignKey('GamePair', on_delete=models.CASCADE, null=True)

    @property
    def finished(self):
        return self.current_page_id == self.end_page_id

    def __str__(self):
        return '{id}: {sp} -> {ep} ({la})'.format(
            id=self.game_id,
            sp=self.start_page_id,
            ep=self.end_page_id,
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
    start_page_id = models.IntegerField()
    end_page_id = models.IntegerField()
    time = models.DateTimeField()
    turn_id = models.AutoField(primary_key=True)


class GamePair(models.Model):
    """
    Ids of all pairs. Uniquely representable structure of game.
    """
    start_page_id = models.IntegerField(default=0)
    end_page_id = models.IntegerField(default=0)
    pair_id = models.AutoField(primary_key=True)
