"""For elasticsearch feature."""

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from ecommerce.models import ProductInventory


@registry.register_document
class ProductInventoryDocument(Document):
    """Document for ProductInventory."""
    product = fields.ObjectField(
        properties={'name': fields.TextField(), 'web_id': fields.TextField()}
    )
    brand = fields.ObjectField(properties={'name': fields.TextField()})

    class Index:
        name = 'productinventory'

    class Django:
        model = ProductInventory

        fields = [
            'id',
            'sku',
            'store_price',
            'sale_price',
            'is_on_sale',
        ]
