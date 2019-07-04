from django.db import models


# Create your models here.

class Game(models.Model):
    first = models.IntegerField(null=True)
    last = models.IntegerField(null=True)
    session_id = models.CharField(unique=True, max_length=100)
    steps = models.IntegerField(null=True)
    ended = models.BooleanField(null=True)

    def __str__(self):
        s = '{sid} ({steps}, {fr} -> {ls})'.format(
            sid=self.session_id,
            steps=self.steps,
            fr=self.first,
        ls=self.last
        )
        return s
