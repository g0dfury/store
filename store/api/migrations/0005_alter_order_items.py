# Generated by Django 3.2.22 on 2023-12-29 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_order_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(blank=True, null=True, through='api.OrderItem', to='api.Product'),
        ),
    ]
