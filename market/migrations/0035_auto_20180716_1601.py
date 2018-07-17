# Generated by Django 2.0.7 on 2018-07-16 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0034_remove_usercoinhistory_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercoinhistory',
            name='charge',
        ),
        migrations.AddField(
            model_name='usercoinhistory',
            name='transaction',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'submission'), (2, 'upvote'), (3, 'referral'), (4, 'store purchase')], null=True),
        ),
    ]