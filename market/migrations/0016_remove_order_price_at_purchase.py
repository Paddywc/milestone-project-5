# Generated by Django 2.0.7 on 2018-07-05 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0015_order_price_at_purchase'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='price_at_purchase',
        ),
    ]
