from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # sample data
        call_command('makemigrations')
        call_command('migrate')
        call_command('loaddata', 'sample_db_category.json')
        call_command('loaddata', 'sample_db_product.json')
        call_command('loaddata', 'sample_db_brand.json')
        call_command('loaddata', 'sample_db_product_attribute.json')
        call_command('loaddata', 'sample_db_product_type.json')
        call_command('loaddata', 'sample_db_product_attribute_value.json')
        call_command('loaddata', 'sample_db_product_inventory.json')
        call_command('loaddata', 'sample_db_media.json')
        call_command('loaddata', 'sample_db_stock.json')
        call_command('loaddata', 'sample_db_product_attribute_values.json')
        call_command('loaddata', 'sample_db_product_type_attribute.json')
        call_command('loaddata', 'sample_db_tax.json')

        # test fixtures
        # call_command('loaddata', 'db_user_fixture.json')
        # call_command('loaddata', 'db_category_fixture.json')
        # call_command('loaddata', 'db_product_fixture.json')
        # call_command('loaddata', 'db_category_product_fixture.json')
        # call_command('loaddata', 'db_type_fixture.json')
        # call_command('loaddata', 'db_brand_fixture.json')
        # call_command('loaddata', 'db_product_inventory_fixture.json')
        # call_command('loaddata', 'db_media_fixture.json')
        # call_command('loaddata', 'db_stock_fixture.json')
        # call_command('loaddata', 'db_product_attribute_fixture.json')
        # call_command('loaddata', 'db_product_attribute_value_fixture.json')
        # call_command('loaddata', 'db_product_attribute_values_fixture.json')
        # call_command('loaddata', 'db_product_type_attribute_fixture.json')


