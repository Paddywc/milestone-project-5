# Generated by Django 2.0.7 on 2018-07-27 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usersuggestions', '0041_auto_20180727_1134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flag',
            name='comment',
        ),
    ]
