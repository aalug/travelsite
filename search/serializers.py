"""Serializers for elastic search feature of ecommerce app."""

from ecommerce.models import ProductAttributeValue, Brand, Category, Product, Media, ProductInventory
from rest_framework import serializers


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for ProductAttributeValue model."""

    class Meta:
        model = ProductAttributeValue
        depth = 2
        exclude = ['id']
        read_only = True


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model."""

    class Meta:
        model = Brand
        fields = ['name']
        read_only = True


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""

    class Meta:
        model = Category
        fields = ['name', 'slug', 'is_active']
        read_only = True


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    class Meta:
        model = Product
        fields = ['name', 'web_id']
        read_only = True
        editable = False


class ProductMediaSerializer(serializers.ModelSerializer):
    """Serializer for Media model."""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ['image', 'alt_text']
        read_only = True
        editable = False

    def get_image(self, obj):
        return obj.image.url


class ProductInventorySerializer(serializers.ModelSerializer):
    """Serializer for ProductInventory model."""
    product = ProductSerializer(many=False, read_only=True)
    media = ProductMediaSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    attributes = ProductAttributeValueSerializer(
        source='attribute_values', many=True, read_only=True
    )

    class Meta:
        model = ProductInventory
        fields = [
            'id',
            'sku',
            'store_price',
            'sale_price',
            'brand',
            'product',
            'is_on_sale',
            'weight',
            'media',
            'attributes',
            'product_type',
        ]
        read_only = True


class ProductInventorySearchSerializer(serializers.ModelSerializer):
    """Serializer for search of ProductInventory."""
    product = ProductSerializer(many=False, read_only=True)
    brand = BrandSerializer(many=False, read_only=True)

    class Meta:
        model = ProductInventory
        fields = [
            'id',
            'sku',
            'store_price',
            'sale_price',
            'is_on_sale',
            'product',
            'brand',
        ]
