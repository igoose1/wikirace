# Generated by Django 2.2.2 on 2019-07-11 09:07

import annoying.fields
from django.conf import settings
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0011_profile_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='settings',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, to='wiki.Settings'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
