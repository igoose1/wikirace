# Generated by Django 2.2.1 on 2019-07-09 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0007_turn'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamestat',
            name='current_page_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='turn',
            name='from_page_id',
            field=models.IntegerField(),
        ),
    ]
