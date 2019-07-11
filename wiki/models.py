from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    start_page_id = models.IntegerField(default=0)
    end_page_id = models.IntegerField(default=0)
    current_page_id = models.IntegerField(null=True, default=None)
    steps = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    last_action_time = models.DateTimeField()

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

    game_id = models.IntegerField()
    from_page_id = models.IntegerField()
    to_page_id = models.IntegerField()
    time = models.DateTimeField()
    turn_id = models.AutoField(primary_key=True)


class Settings(models.Model):
    difficulty = models.IntegerField()
    name = models.TextField(default="no name", max_length=16)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    settings = models.OneToOneField(Settings, on_delete=models.CASCADE)
