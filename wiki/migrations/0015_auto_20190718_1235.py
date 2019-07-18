# Generated by Django 2.2.3 on 2019-07-18 09:35

from django.db import migrations, models
import django.db.models.deletion


def create_multiplayers(apps, schema_editor):
    # We can't import models directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Game = apps.get_model('wiki', 'Game')
    MultiplayerPair = apps.get_model('wiki', 'MultiplayerPair')
    for game in Game.objects.all():
        game.multiplayer = MultiplayerPair.create(game_pair=game.game_pair)
        game.save()


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0014_game_surrendered'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiplayerPair',
            fields=[
                ('multiplayer_id', models.AutoField(primary_key=True, serialize=False)),
                ('multiplayer_key', models.CharField(blank=True, default='', max_length=64)),
                ('game_pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.GamePair')),
            ],
            options={
                'unique_together': {('multiplayer_key',)},
            },
        ),
        migrations.AddField(
            model_name='game',
            name='multiplayer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wiki.MultiplayerPair'),
        ),
        migrations.RunPython(create_multiplayers),
    ]