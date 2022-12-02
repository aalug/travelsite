from django.views.generic import TemplateView, FormView

from ecommerce.models import Product, ProductInventory, Media


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'home.html'

    @staticmethod
    def get_products_data():
        """Return three random products with images."""
        products = Product.objects.filter(is_active=True).order_by('?')[:3]
        products_data = []
        for product in products:
            product_inventory = ProductInventory.objects.filter(product=product)[0]
            image = Media.objects.filter(product_inventory=product_inventory, is_feature=True)
            if image:
                image = image[0]
            products_data.append(
                {'product': product, 'image': image}
            )
        return products_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products_data'] = self.get_products_data()
        return context
