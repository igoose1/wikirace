from django.db import models
from django.contrib.sessions.models import Session
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
import hashlib


class MultiplayerPair(models.Model):
    from_page_id = models.IntegerField()
    to_page_id = models.IntegerField()
    game_id = models.AutoField(primary_key=True)
    game_key = models.CharField(default='', max_length=64)

    def game_key_calculate(self):
        if self.game_key != '':
            return
        suffix = settings.SECRET_KEY
        hashed_string = None
        counter = 0
        while hashed_string is None or MultiplayerPair.objects.filter(game_key=self.game_key).count() > 0:
            counter += 1
            suffix += 'a'
            hashed_string = hashlib.sha256((str(self.game_id) + suffix).encode()).hexdigest()
            self.game_key = hashed_string[:min(6 + counter // 1024, 16)]
        self.save()


@receiver(post_save, sender=MultiplayerPair)
def create_multiplayer_key(sender, instance, created, **kwargs):
    if created:
        instance.game_key_calculate()


class Game(models.Model):
    multiplayer = models.ForeignKey(MultiplayerPair, null=True,
                                    on_delete=models.SET_NULL)
    session = models.ForeignKey(Session, null=True,
                                on_delete=models.SET_NULL)
    session_key = models.CharField(default='', max_length=128)
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
