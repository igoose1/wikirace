# Generated by Django 2.2.3 on 2019-07-17 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0013_auto_20190717_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='surrendered',
            field=models.BooleanField(default=False),
        ),
    ]
