# Generated by Django 2.0.7 on 2018-07-06 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersuggestions', '0003_auto_20180706_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggestion',
            name='details',
            field=models.CharField(max_length=200),
        ),
    ]