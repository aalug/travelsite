# Generated by Django 4.1.1 on 2022-10-28 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0006_alter_productinventory_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductTypeAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_attribute', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productattribute', to='ecommerce.productattribute')),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='producttype', to='ecommerce.producttype')),
            ],
            options={
                'unique_together': {('product_attribute', 'product_type')},
            },
        ),
    ]
