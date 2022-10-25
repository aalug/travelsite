import pytest
from django.core.management import call_command


@pytest.fixture
def create_test_user(django_user_model):
    """Creates and returns a user."""
    user = django_user_model.objects.create_user(
        email='test_user@example.com',
        username='TestName',
        password='asdasd123123'
    )
    user.is_active = True
    user.save()

    return user


@pytest.fixture
def create_test_superuser(django_user_model):
    """Creates and returns a superuser."""
    user = django_user_model.objects.create_superuser(
        email='admin_user@example.com',
        username='AdminName',
        password='asdasd123123'
    )
    return user


@pytest.fixture(scope='session')
def db_fixture_setup(django_db_setup, django_db_blocker):
    """Load DB data fixtures."""
    with django_db_blocker.unblock():
        call_command('loaddata', 'db_category_fixture.json')
        call_command('loaddata', 'db_product_fixture.json')
        call_command('loaddata', 'db_type_fixture.json')
        call_command('loaddata', 'db_brand_fixture.json')
        call_command('loaddata', 'db_product_inventory_fixture.json')
        call_command('loaddata', 'db_media_fixture.json')
        call_command('loaddata', 'db_stock_fixture.json')
        call_command('loaddata', 'db_product_attribute_fixture.json')
        call_command('loaddata', 'db_product_attribute_value_fixture.json')
        call_command('loaddata', 'db_product_attribute_values_fixture.json')
