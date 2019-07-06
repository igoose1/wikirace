from django.db import models


# Create your models here.

class Game(models.Model):
    first = models.IntegerField(null=True)
    last = models.IntegerField(null=True)
    session_id = models.CharField(unique=True, max_length=100)
    steps = models.IntegerField(default=0)
    ended = models.BooleanField(default=False)

    def __str__(self):
        s = '{sid} ({steps}, {fr} -> {ls})'.format(
            sid=self.session_id,
            steps=self.steps,
            fr=self.first,
        ls=self.last
        )
        return s


class GameStat(models.Model):
    game_id = models.AutoField(primary_key=True)
    start_page_id = models.IntegerField(default=0)
    end_page_id = models.IntegerField(default=0)
    steps = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True)
    last_action_time = models.DateTimeField()

    def __str__(self):
        return '{id}: {sp} -> {ep} ({la})'.format(
            id=self.game_id,
            sp=self.start_page_id,
            ep=self.end_page_id,
            la=self.last_action_time
        )
