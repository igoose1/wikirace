# Generated by Django 2.2.4 on 2020-01-02 08:59

from django.db import migrations, models
import django.db.models.deletion
import wiki.models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0023_auto_20191231_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='difficulty',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='usersettings',
            name='rate',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='GameStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'class_type',
                    models.CharField(
                        choices=[
                            (wiki.models.GameTypes('random'), 'random'),
                            (wiki.models.GameTypes('easy'), 'easy'),
                            (wiki.models.GameTypes('medium'), 'medium'),
                            (wiki.models.GameTypes('hard'), 'hard'),
                            (wiki.models.GameTypes('trial'), 'trial'),
                            (wiki.models.GameTypes('by_id'), 'by_id')
                        ],
                        max_length=64)),
                ('rate_delta', models.FloatField(default=0)),
                ('hops', models.IntegerField(default=0)),
                ('time', models.DurationField()),
                (
                    'game_pair',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='wiki.GamePair'
                    )
                ),
                (
                    'trial_id',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='wiki.Trial'
                    )
                ),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.UserSettings')),
            ],
        ),
    ]
