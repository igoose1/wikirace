# Generated by Django 2.2.2 on 2019-07-17 08:46

from django.db import migrations, models
import django.db.models.deletion


def create_game_pairs(apps, schema_editor):
    # We can't import models directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Game = apps.get_model('wiki', 'Game')
    GamePair = apps.get_model('wiki', 'GamePair')
    for game in Game.objects.all():
        game.game_pair = GamePair.objects.get_or_create(
            start_page_id=game.start_page_id,
            end_page_id=game.end_page_id,
        )[0]
        game.save()


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0010_auto_20190710_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='GamePair',
            fields=[
                ('pair_id', models.AutoField(primary_key=True, serialize=False)),
                ('start_page_id', models.IntegerField(default=0)),
                ('end_page_id', models.IntegerField(default=0)),
            ],
            options={
                'unique_together': {('start_page_id', 'end_page_id')},
            },
        ),
        migrations.AddField(
            model_name='game',
            name='game_pair',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wiki.GamePair'),
        ),
        migrations.RunPython(create_game_pairs),
    ]
