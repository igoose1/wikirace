# Generated by Django 2.2.2 on 2019-07-06 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_gamestat'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100, null=True)),
                ('time', models.TimeField(null=True)),
            ],
        ),
    ]
