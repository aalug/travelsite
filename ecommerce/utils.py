"""Helper functions for views in ecommerce app."""
from django.shortcuts import get_object_or_404

from ecommerce.models import ProductAttributeValues, Category, ProductInventory, Media, Stock


def size_sorting_key(element):
    """Key for sorting sizes."""
    sizes = ['xs', 's', 'm', 'l', 'xl']
    return sizes.index(element)


def get_all_products_attribute_values(product_inventory):
    """Gets and returns attribute values for products
       inventories to display with all other data. It gets
       ProductInventory as an argument but then gets
       all Product objects related to it - to get all
       attribute values, bot just the ones connected to
       this ProductInventory."""
    product = product_inventory.product
    all_products_inventories = ProductInventory.objects.filter(product=product)
    attribute_values = {}

    for prod_inv in all_products_inventories:
        values = ProductAttributeValues.objects.filter(productinventory=prod_inv).distinct()
        for v in values:
            x = str(v).split(' : ')
            attr_name = x[0]
            attr_value = x[1]
            if attr_name not in attribute_values:
                attribute_values[attr_name] = [attr_value]
            else:
                val = attribute_values.get(attr_name)
                if attr_value not in val:
                    val.append(attr_value)
                attribute_values[attr_name] = val

    # sorting sizes
    if 'size' in attribute_values:
        values = attribute_values.get('size')
        values.sort(key=size_sorting_key)
        attribute_values['size'] = values

    return attribute_values


def get_specific_attribute_values(product_inventory):
    """Gets and returns ProductAttributeValues for a specific
       ProductInventory, not all values associated with this Product
       like function get_all_products_attribute_values."""
    attribute_values = {}
    values = ProductAttributeValues.objects.filter(productinventory=product_inventory)

    for v in values:
        x = str(v).split(' : ')
        attr_name = x[0]
        attr_value = x[1]
        attribute_values[attr_name] = attr_value

    return attribute_values


def get_categories_with_parents_and_children():
    """Helper function for getting categories, but with
       distinction, which categories are parents and which
       ones are children."""
    categories = Category.objects.filter(is_active=True)
    categories_dict = {}

    for category in categories:
        if not category.parent:
            categories_dict.update({
                category: []
            })
        else:
            categories_dict[category.parent].append(category)

    return categories_dict


def get_filters(slug: str=None) -> dict[str: str]:
    """Method gets and returns filters. If argument 'slug' is passed,
       function will return filters appropriate to category with that slug.
       If 'slug' will be left as None - function will return all filters."""
    if slug:
        attrs = ProductInventory.objects.filter(product__category__slug=slug).values(
            'attribute_values__product_attribute__name', 'attribute_values__attribute_value').distinct()
    else:
        attrs = ProductInventory.objects.all().values(
            'attribute_values__product_attribute__name', 'attribute_values__attribute_value').distinct()

    filters = {}
    attr_name = 'attribute_values__product_attribute__name'
    attr_value = 'attribute_values__attribute_value'

    for attr in attrs:
        if attr[attr_name] in filters:
            value = filters.get(attr[attr_name])
            value.append(attr[attr_value])
            filters[attr[attr_name]] = value
        else:
            filters[attr[attr_name]] = [attr[attr_value]]

    # sorting sizes
    if 'size' in filters:
        values = filters.get('size')
        values.sort(key=size_sorting_key)
        filters['size'] = values

    return filters


def get_queryset_with_filters(request_get, slug=None, products=None) -> list[tuple]:
    """Method gets and returns products with applied filters.
       If the filters are checked - it will return filtered data,
       if not - it will return all products that are associated
       with this category - if the 'slug' argument was passed,
       on the other hand - if 'products' was passed, function will
       apply filters to this queryset.
       Required is passing 'request_get' with either 'slug' or 'products'."""

    if not slug and not products:
        raise TypeError('Not enough arguments - required is either slug or products.')
    elif slug and products:
        raise TypeError('Too many arguments - required is either slug or products.')

    filter_arguments = []
    if slug:
        filtered_products = ProductInventory.objects.filter(product__category__slug=slug)
    else:
        filtered_products = products

    if request_get:  # there are filters to apply
        for key, value in request_get.items():
            if key != 'query':  # query is connected to searching, not filtering
                filter_arguments.append(value)

        from django.db.models import Count

        filtered_products = filtered_products.filter(
            attribute_values__attribute_value__in=filter_arguments).annotate(
            num_tags=Count('attribute_values')).filter(num_tags=len(filter_arguments))

    products_data = []
    for product_inventory in filtered_products:
        units = get_object_or_404(Stock, product_inventory=product_inventory).units
        image = Media.objects.filter(product_inventory=product_inventory, is_feature=True)
        if image:
            image = image[0]
        attribute_values = get_all_products_attribute_values(product_inventory)
        data = (product_inventory, units, image, attribute_values)
        products_data.append(data)
    return products_data
