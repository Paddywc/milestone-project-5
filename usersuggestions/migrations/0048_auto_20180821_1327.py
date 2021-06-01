# Generated by Django 2.0.7 on 2018-08-21 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersuggestions', '0047_auto_20180820_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flag',
            name='reason',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Spam/Duplicate'), (1, 'Hate Speech'), (2, 'Graphic Content'), (3, 'Harassment or Bullying')]),
        ),
    ]