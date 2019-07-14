from django.db import models


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


class UserGame(models.Model):
    game_id = models.AutoField(primary_key=True)
    autor_name = models.CharField(default='Анонимно', max_length=30)
    from_page_id = models.IntegerField()
    to_page_id = models.IntegerField()
    likes = models.IntegerField(default=0)
    shortest_path_len = models.IntegerField(null=True)
    time = models.DateTimeField()


class Trial(models.Model):
    game_id = models.AutoField(primary_key=True)
    trial_name = models.CharField(default='испытание', max_length=200)
    from_page_id = models.IntegerField()
    to_page_id = models.IntegerField()

    def __str__(self):
        return '{trial_name}, ind = {game_id}, path: {from_page_id} -> {to_page_id}'.format(
            trial_name=self.trial_name,
            game_id=self.game_id,
            from_page_id=self.from_page_id,
            to_page_id=self.to_page_id
        )
