"""Views for ecommerce app."""

import json

from elasticsearch_dsl import Q

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, TemplateView

from .models import Category, Product, ProductInventory, Stock, Media
from .utils import get_all_products_attribute_values, get_categories_with_parents_and_children, size_sorting_key, \
    get_specific_attribute_values, get_filters, get_queryset_with_filters

from search.documents import ProductInventoryDocument
from search.serializers import ProductInventorySearchSerializer


class MainShopPageView(TemplateView):
    """View for main page of the ecommerce app."""
    template_name = 'ecommerce/main_shop_page.html'

    @staticmethod
    def get_products_data():
        """Method gets 3 random categories and 3 products
           of each of them and returns list which contains
           3 tuples - every one contains data for each of
           3 chosen categories."""
        import random
        categories = Category.objects.filter(is_active=True)
        random_categories = []
        while len(random_categories) < 3:
            rand_cat = random.choice(categories)
            if rand_cat not in random_categories:
                random_categories.append(rand_cat)

        all_products = []
        for category in random_categories:
            products = Product.objects.filter(category=category, is_active=True)[:3]

            for product in products:
                product_inventory = ProductInventory.objects.filter(product=product)[0]
                image = Media.objects.filter(product_inventory=product_inventory, is_feature=True)
                if image:
                    image = image[0]
                units = get_object_or_404(Stock, product_inventory=product_inventory)
                attribute_values = get_all_products_attribute_values(product_inventory)

                # This works because on this website won't be many products, so it can still be efficient
                all_products.append((category, product_inventory, image, units, attribute_values))

        category1_items = []
        category2_items = []
        category3_items = []

        # sorting data and adding to appropriate list (by category)
        for item in all_products:
            if item[0] == random_categories[0]:
                category1_items.append(item)
            elif item[0] == random_categories[1]:
                category2_items.append(item)
            else:
                category3_items.append(item)

        return [
            category1_items,
            category2_items,
            category3_items
        ]

    @staticmethod
    def get_products_on_sale():
        """Gets and returns all active products that are currently on sale."""
        product_inventories = ProductInventory.objects.filter(is_on_sale=True, is_active=True)
        products_data = []
        for product_inv in product_inventories:
            category = product_inv.product.category
            image = Media.objects.filter(product_inventory=product_inv, is_feature=True)
            if image:
                image = image[0]
            units = get_object_or_404(Stock, product_inventory=product_inv)
            attribute_values = get_all_products_attribute_values(product_inv)
            data = (category, product_inv, image, units, attribute_values)
            products_data.append(data)

        return products_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        while True:
            data = self.get_products_data()
            if len(data[0]) > 0 and len(data[1]) > 0 and len(data[2]) > 0:
                break

        context['on_sale'] = self.get_products_on_sale()
        context['all_categories'] = get_categories_with_parents_and_children()
        context['category1_items'] = data[0]
        context['category2_items'] = data[1]
        context['category3_items'] = data[2]
        return context


class ProductsByCategoryView(ListView):
    """View for fetching products by category (send in as "slug")."""
    template_name = 'ecommerce/products_by_category.html'
    context_object_name = 'products_data'
    filter_presence = True

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        request_get = self.request.GET
        return get_queryset_with_filters(request_get=request_get, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        context['all_categories'] = get_categories_with_parents_and_children()
        context['category'] = category

        filters = get_filters(self.kwargs.get('slug'))
        if len(filters) > 0:
            context['filter_presence'] = True
        else:
            context['filter_presence'] = False

        context['filters'] = filters

        return context


class ProductDetailView(TemplateView):
    """View for handling pages with details about a product."""
    template_name = 'ecommerce/product_details.html'

    # If True that means that there are attribute values to choose from
    is_to_choose = False

    def get_products_data(self):
        """Method gets and returns product details for a specific
           product (based on 'slug' value in kwargs)."""
        products_data = []
        slug = self.kwargs.get('slug')
        product = get_object_or_404(Product, slug=slug)
        product_inventories = ProductInventory.objects.filter(product=product)

        def get_data(product_inv):
            units = get_object_or_404(Stock, product_inventory=product_inv).units
            attr_values = get_specific_attribute_values(product_inv)
            if 'size' in attr_values or 'language' in attr_values:
                self.is_to_choose = True
            return product_inventory, attr_values, units

        for product_inventory in product_inventories:
            data = get_data(product_inventory)
            products_data.append(data)

        return products_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        title = slug.replace('-', ' ')
        products_data = self.get_products_data()
        images = Media.objects.filter(product_inventory=products_data[0][0])

        context['is_to_choose'] = self.is_to_choose
        context['title'] = title
        context['products_data'] = products_data
        context['images'] = images
        context['product'] = get_object_or_404(Product, slug=slug)

        return context


class SearchProductInventoryView(View):
    productinventory_serializer = ProductInventorySearchSerializer
    search_document = ProductInventoryDocument

    @staticmethod
    def get_products_from_serializer_data(serializer_data):
        json_data = json.dumps(serializer_data)
        dict_data = json.loads(json_data)
        all_products = []

        for data in dict_data:
            data_id = data.get('id')
            units = get_object_or_404(Stock, product_inventory__id=data_id).units
            image = Media.objects.filter(product_inventory__id=data_id, is_feature=True)
            if image:
                image = image[0]
            product_inventory = get_object_or_404(ProductInventory, id=data_id)
            attr_values = get_all_products_attribute_values(product_inventory)
            product_data = (product_inventory, units, image, attr_values)
            all_products.append(product_data)
        return all_products

    def get(self, request):
        query = request.GET.get('query')
        try:
            q = Q(
                'multi_match',
                query=query,
                fields=['product.name', 'product_type', 'product.web_id', 'brand.name'],
                fuzziness='auto',
            ) & Q(
                should=[
                    Q('match'),
                ],
                minimum_should_match=1,
            )

            search = self.search_document.search().query(q)
            response = search.execute()

            serializer = self.productinventory_serializer(response, many=True)

        except Exception as e:
            return HttpResponse(e, status=500)

        else:
            all_products = self.get_products_from_serializer_data(serializer.data)
            if len(self.request.GET) > 1:  # there is more than just query=...
                names = []
                for product in all_products:
                    name = product[0]
                    names.append(name)
                prods_invs = ProductInventory.objects.filter(product__name__in=names)
                all_products = get_queryset_with_filters(request_get=self.request.GET, products=prods_invs)
            context = {
                'all_categories': get_categories_with_parents_and_children(),
                'filters': get_filters(),
                'products_data': all_products
            }

        return render(request, 'ecommerce/search.html', context)
