# Generated by Django 2.2.2 on 2019-07-14 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0010_auto_20190710_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiplayerPair',
            fields=[
                ('from_page_id', models.IntegerField()),
                ('to_page_id', models.IntegerField()),
                ('game_id', models.CharField(max_length=30, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='multiplayer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wiki.MultiplayerPair'),
        ),
    ]
