# Generated by Django 2.2.4 on 2020-01-05 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0028_auto_20200104_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='curr_game_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='usersettings',
            name='history_json',
            field=models.CharField(default='', max_length=512),
        ),
    ]