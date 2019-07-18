# Generated by Django 2.2.2 on 2019-07-17 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('wiki', '0013_auto_20190717_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.Session'),
        ),
        migrations.AddField(
            model_name='game',
            name='session_key',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.CreateModel(
            name='MultiplayerPair',
            fields=[
                ('game_id', models.AutoField(primary_key=True, serialize=False)),
                ('game_key', models.CharField(default='', max_length=64)),
                ('game_pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.GamePair')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='multiplayer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wiki.MultiplayerPair'),
        ),
    ]