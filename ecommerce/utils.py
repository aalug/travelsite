"""Helper functions for views in ecommerce app."""

from ecommerce.models import ProductAttributeValues, Category


def get_products_attribute_values(product_inventory):
    """Gets and returns attribute values for products
    inventories to display with all other data."""
    values = ProductAttributeValues.objects.filter(productinventory=product_inventory)
    attribute_values = {}

    for v in values:
        x = str(v).split(' : ')
        attr_name = x[0]
        attr_value = x[1]
        if attr_name not in attribute_values:
            attribute_values[attr_name] = [attr_value]
        else:
            val = attribute_values[attr_name]
            val.append(attr_value)
            attribute_values[attr_name] = val

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
