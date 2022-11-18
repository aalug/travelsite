"""Helper functions for views in ecommerce app."""

from ecommerce.models import ProductAttributeValues, Category, ProductInventory


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
