# Generated by Django 4.1.1 on 2022-11-30 23:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ecommerce', '0036_remove_placedorder_order_items_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='orderitem',
            unique_together={('user', 'product_inventory')},
        ),
    ]