# Generated by Django 2.2.4 on 2019-12-31 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0020_auto_20191231_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='vk_id',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usersettings',
            name='_name',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
