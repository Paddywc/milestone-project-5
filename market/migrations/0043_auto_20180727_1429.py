# Generated by Django 2.0.7 on 2018-07-27 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0042_auto_20180727_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='postcode',
            field=models.CharField(max_length=20),
        ),
    ]
