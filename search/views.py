from django.http import HttpResponse

from ecommerce.models import (
    Category,
    Product,
    ProductInventory
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from elasticsearch_dsl import Q

from search.documents import ProductInventoryDocument
from search.serializers import CategorySerializer, ProductSerializer, ProductInventorySerializer, \
    ProductInventorySearchSerializer


class CategoryList(APIView):
    """Return list of all categories."""

    def get(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)


class ProductByCategory(APIView):
    """Return product by category."""

    def get(self, request, query=None):
        queryset = Product.objects.filter(category__slug=query)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductInventoryByWebId(APIView):
    """Return Sub Product by WebId."""

    def get(self, request, query=None):
        queryset = ProductInventory.objects.filter(product__web_id=query)
        serializer = ProductInventorySerializer(queryset, many=True)
        return Response(serializer.data)


class SearchProductInventory(APIView, LimitOffsetPagination):
    """APIView for search of ProductInventory."""
    productinventory_serializer = ProductInventorySearchSerializer
    search_document = ProductInventoryDocument

    def get(self, request, query=None):
        try:
            q = Q(
                'multi_match',
                query=query,
                fields=['product.name', 'product.web_id', 'brand.name'],
                fuzziness='auto',
            ) & Q(
                should=[
                    Q('match'),
                ],
                minimum_should_match=1,
            )

            search = self.search_document.search().query(q)
            response = search.execute()

            results = self.paginate_queryset(response, request, view=self)
            serializer = self.productinventory_serializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return HttpResponse(e, status=500)
