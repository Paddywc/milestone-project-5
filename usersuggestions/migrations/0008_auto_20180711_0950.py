# Generated by Django 2.0.7 on 2018-07-11 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usersuggestions', '0007_auto_20180711_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upvote',
            name='suggestion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='usersuggestions.Suggestion'),
        ),
    ]