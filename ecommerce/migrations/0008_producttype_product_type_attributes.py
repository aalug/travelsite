# Generated by Django 4.1.1 on 2022-10-28 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0007_producttypeattribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttype',
            name='product_type_attributes',
            field=models.ManyToManyField(related_name='product_type_attributes', through='ecommerce.ProductTypeAttribute', to='ecommerce.productattribute'),
        ),
    ]