# Generated by Django 2.0.7 on 2018-07-11 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usersuggestions', '0006_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suggestion',
            old_name='is_suggestion',
            new_name='is_feature',
        ),
    ]
