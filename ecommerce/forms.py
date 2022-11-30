from django.forms import ModelForm

from ecommerce.models import Order


class OrderForm(ModelForm):
    """Form for entering data to place an order."""

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email',
                  'address', 'country', 'state', 'city', 'pin_code']
