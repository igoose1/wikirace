from django.db import models


# Create your models here.

class Game(models.Model):
    first = models.IntegerField(null=True)
    last = models.IntegerField(null=True)
    session_id = models.CharField(unique=True, max_length=100)
    steps = models.IntegerField(null=True)
    ended = models.BooleanField(null=True)

    def __str__(self):
        s = "first: "+str(self.first)+"\nlast :"+str(self.last)+"\nsteps :"+str(self.steps)
        return s
