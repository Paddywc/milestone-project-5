# Generated by Django 2.0.7 on 2018-07-16 10:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0025_usercoinhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
