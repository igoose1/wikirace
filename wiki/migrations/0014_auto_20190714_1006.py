# Generated by Django 2.2.3 on 2019-07-14 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0013_auto_20190712_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamepair',
            name='id',
        ),
        migrations.AlterField(
            model_name='gamepair',
            name='pair_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
