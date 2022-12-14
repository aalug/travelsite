# Generated by Django 4.1.1 on 2022-10-25 21:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0004_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='format: required, unique, max-255', max_length=255, unique=True, verbose_name='product attribute name')),
                ('description', models.TextField(help_text='format: required', verbose_name='product attribute description')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_value', models.CharField(help_text='format: required, max-255', max_length=255, verbose_name='attribute value')),
                ('product_attribute', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_attribute', to='ecommerce.productattribute')),
            ],
        ),
        migrations.AlterField(
            model_name='productinventory',
            name='retail_price',
            field=models.DecimalField(decimal_places=2, error_messages={'name': {'max_length': '{PRICE_RANGE_ERROR_MSG}.'}}, help_text='format: maximum price 999.99', max_digits=5, verbose_name='recommended retail price'),
        ),
        migrations.CreateModel(
            name='ProductAttributeValues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributevalues', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attributevaluess', to='ecommerce.productattributevalue')),
                ('productinventory', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productattributevaluess', to='ecommerce.productinventory')),
            ],
            options={
                'unique_together': {('attributevalues', 'productinventory')},
            },
        ),
        migrations.AddField(
            model_name='productinventory',
            name='attribute_values',
            field=models.ManyToManyField(related_name='product_attribute_values', through='ecommerce.ProductAttributeValues', to='ecommerce.productattributevalue'),
        ),
    ]
