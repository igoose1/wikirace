# Generated by Django 2.2.2 on 2019-07-15 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0014_auto_20190715_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='session_key',
            field=models.CharField(default='', max_length=128),
        ),
    ]
