# Generated by Django 2.2.3 on 2019-07-16 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0010_auto_20190710_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='possible_path',
            field=models.TextField(default=''),
        ),
    ]
