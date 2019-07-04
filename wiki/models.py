from django.db import models


# Create your models here.

class Game(models.Model):
    first = models.IntegerField()
    last = models.IntegerField()
    session_id = models.CharField(unique=True, max_length = 100)
    steps = models.IntegerField()
    ended = models.BooleanField()
