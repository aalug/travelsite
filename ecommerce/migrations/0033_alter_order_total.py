# Generated by Django 4.1.1 on 2022-11-28 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0032_cart_total_tax_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]