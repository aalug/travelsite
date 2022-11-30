from ecommerce.models import Cart


def get_cart_quantity(request):
    """Gets and returns as dictionary cart quantity of a logged-in user"""
    try:
        quantity = Cart.objects.get(user=request.user).quantity
    except Exception:
        quantity = 0
    return dict(cart_quantity=quantity)

