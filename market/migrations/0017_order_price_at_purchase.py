# Generated by Django 2.0.7 on 2018-07-05 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0016_remove_order_price_at_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='price_at_purchase',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
            preserve_default=False,
        ),
    ]
