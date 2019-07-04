from django.db import models

# Create your models here.

class Game(models.Model):
    first = models.CharField(max_length = 100)
    last = models.CharField(max_length = 100)
    steps = models.IntegerField()
    ended = models.BooleanField()

