# Generated by Django 2.0.7 on 2018-07-11 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersuggestions', '0017_suggestionadminpage_github_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggestionadminpage',
            name='github_branch',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
