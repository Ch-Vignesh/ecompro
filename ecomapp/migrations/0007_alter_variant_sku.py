# Generated by Django 4.2 on 2025-01-10 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0006_remove_value_variant_product_seller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='sku',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
