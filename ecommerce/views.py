"""Views for ecommerce app."""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from elasticsearch_dsl import Q

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, TemplateView, RedirectView, DetailView, FormView

from accounts.models import UserProfile
from .forms import OrderForm
from .models import Category, Product, ProductInventory, Stock, Media, Cart, OrderItem, Tax, Order, Payment, PlacedOrder
from .utils import get_all_products_attribute_values, get_categories_with_parents_and_children, \
    get_specific_attribute_values, get_filters, get_queryset_with_filters, generate_order_number, \
    generate_transaction_id, send_notification

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
    """View for handling searching for products. It gets data
       from request.GET and returns data with help of elasticsearch
       and other features from search app."""
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


class CartView(LoginRequiredMixin, TemplateView):
    """Cart view, gets OrderItem objects and additional data
       such us images and attribute values. If there is
       no OrderItems is_empty is set to False."""
    template_name = 'ecommerce/cart.html'

    def get_cart_data(self) -> list[tuple[dict[str: any], dict[str: any], dict[str: any]]]:
        """Method gets additional data for every OrderItem,
           such as images (Media)."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = OrderItem.objects.filter(cart=cart)
        data = []
        if cart_items:
            for item in cart_items:
                image = Media.objects.filter(product_inventory=item.product_inventory, is_feature=True)
                attribute_values = get_specific_attribute_values(item.product_inventory)
                if image:
                    image = image[0]
                d = ({'cart_item': item}, {'image': image}, {'attribute_values': attribute_values})
                data.append(d)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_cart_data()
        context['is_empty'] = len(cart_items) == 0
        context['cart_items'] = cart_items
        context['cart'] = get_object_or_404(Cart, user=self.request.user)
        return context


class AddToCartView(LoginRequiredMixin, RedirectView):
    """RedirectView that gets sku of choosem ProductInventory and then
       1. Fetches Cart if it exists or creates one if it does not.
       2. Fetches OrderItem (and increments values) or creates one.
       3. Redirects to cart page."""

    @staticmethod
    def if_cart_not_created(product_inventory, user, cart):
        try:
            # if there is OrderItem, that means that user is adding the same
            # item to the cart for the second, third... time
            order_item = OrderItem.objects.get(cart=cart, product_inventory=product_inventory)
        except OrderItem.DoesNotExist:
            if product_inventory.is_on_sale:
                price = product_inventory.sale_price
            else:
                price = product_inventory.store_price

            order_item = OrderItem.objects.create(
                user=user,
                cart=cart,
                product_inventory=product_inventory,
                price=price,
                amount=price  # quantity is 1, so the price = amount
            )
            order_item.save()
        else:
            order_item.quantity += 1
            order_item.amount += order_item.price
            order_item.save()
        finally:
            cart.total_amount += order_item.price
            cart.quantity += 1
            cart.save()

    @staticmethod
    def if_cart_created(product_inventory, user, cart):
        """Cart was just created -> there is no OrderItems."""
        if product_inventory.is_on_sale:
            price = product_inventory.sale_price
        else:
            price = product_inventory.store_price

        order_item = OrderItem.objects.create(
            user=user,
            cart=cart,
            product_inventory=product_inventory,
            price=price,
            amount=price  # quantity is 1, so the price = amount
        )
        order_item.save()
        cart.total_amount += order_item.price
        cart.quantity += 1
        cart.save()

    def get_or_create_cart_and_order_item(self):
        sku = self.request.GET.get('sku')
        product_inventory = get_object_or_404(ProductInventory, sku=sku)
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            self.if_cart_created(product_inventory, user, cart)
        else:
            self.if_cart_not_created(product_inventory, user, cart)

    def get_redirect_url(self):
        self.get_or_create_cart_and_order_item()
        return reverse_lazy('cart')


class DeleteOrderItemView(RedirectView):
    """View removes relation between OrderItem and user's cart
       and updates other cart values."""

    def delete_order_item(self):
        """Method fetches (sku) OrderItem and removes it from user's cart."""
        sku = self.kwargs.get('sku')
        to_delete_item = get_object_or_404(OrderItem,
                                           product_inventory__sku=sku,
                                           user=self.request.user)
        cart = to_delete_item.cart
        # update cart
        cart.quantity -= to_delete_item.quantity
        cart.total_amount -= to_delete_item.amount
        cart.save()
        to_delete_item.delete()

    def get_redirect_url(self, **kwargs):
        self.delete_order_item()
        return reverse_lazy('cart')


class DeleteCartView(RedirectView):
    """View deletes cart of logged-in user."""

    def delete_cart_items(self):
        """Delete all OrderItem objects from Cart."""
        OrderItem.objects.filter(cart__user=self.request.user).delete()
        cart = get_object_or_404(Cart, user=self.request.user)
        cart.quantity = 0
        cart.total_amount = 0
        cart.total_tax_amount = 0
        cart.save()

    def get_redirect_url(self):
        self.delete_cart_items()
        return reverse_lazy('cart')


class OrderConfirmationView(LoginRequiredMixin, TemplateView):
    """View handles order confirmation."""
    template_name = 'ecommerce/order_summary.html'

    def get_data(self):
        cart = get_object_or_404(Cart, user=self.request.user)
        order_items = OrderItem.objects.filter(cart=cart)
        tax_data = []
        for item in order_items:
            taxes = Tax.objects.filter(product_type=item.product_inventory.product_type)
            attribute_values = get_specific_attribute_values(item.product_inventory)
            for tax in taxes:
                amount = item.amount * tax.tax_percentage / 100
                data = (item, tax, amount, attribute_values)
                tax_data.append(data)

        return tax_data

    def get_total_amount_with_taxes(self):
        """Returns a tuple of total amount and total tax amount."""
        data = self.get_data()
        total_tax_amount = 0
        for item, tax, amount, attribute_values in data:
            total_tax_amount += amount

        cart = get_object_or_404(Cart, user=self.request.user)
        total_cart_amount = cart.total_amount
        cart.total_tax_amount = total_tax_amount
        cart.save()

        return total_cart_amount, total_tax_amount

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tax_data = self.get_data()
        total_cart_amount, total_tax_amount = self.get_total_amount_with_taxes()
        context['tax_data'] = tax_data
        context['total_amount'] = total_cart_amount + total_tax_amount
        return context


class CheckOutView(LoginRequiredMixin, FormView):
    """View for placing an order."""
    template_name = 'ecommerce/checkout.html'
    success_url = reverse_lazy('payment')
    form_class = OrderForm

    def get_initial(self):
        initial = super().get_initial()
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        initial['email'] = self.request.user.email
        initial['address'] = user_profile.address
        initial['country'] = user_profile.country
        initial['state'] = user_profile.state
        initial['city'] = user_profile.city
        initial['pin_code'] = user_profile.pin_code
        return initial

    def form_valid(self, form):
        cart = get_object_or_404(Cart, user=self.request.user)
        order = Order()
        order.first_name = form.cleaned_data['first_name']
        order.last_name = form.cleaned_data['last_name']
        order.phone = form.cleaned_data['phone']
        order.email = form.cleaned_data['email']
        order.address = form.cleaned_data['address']
        order.country = form.cleaned_data['country']
        order.state = form.cleaned_data['state']
        order.city = form.cleaned_data['city']
        order.pin_code = form.cleaned_data['pin_code']
        order.user = self.request.user
        order.total = cart.total_amount + cart.total_tax_amount
        order.total_tax = cart.total_tax_amount
        order.payment_method = self.request.POST['payment-method']
        order.order_number = generate_order_number(self.request.user.id)
        order.save()
        return super().form_valid(form)


class PaymentView(LoginRequiredMixin, View):
    """View for faking payment process - just waits few seconds
       and proceeds with ordering process."""
    template_name = 'ecommerce/payment.html'

    def create_payment(self):
        order = Order.objects.filter(user=self.request.user).order_by('-created_at')[0]
        amount = order.total
        payment = Payment.objects.create(
            user=self.request.user,
            transaction_id=generate_transaction_id(order),
            payment_method=str(order.payment_method),
            amount=amount,
            status='Completed'
        )
        order.status = 'Accepted'
        order.is_ordered = True
        payment.save()
        order.save()

    def get(self, request, *args, **kwargs):
        self.create_payment()
        return render(request, self.template_name)


class OrderPlacedView(LoginRequiredMixin, View):
    """View finished ordering page."""
    template_name = 'ecommerce/order_placed.html'

    def create_placed_order(self):
        """Create PlaceOrder for storing history of purchases."""
        cart = get_object_or_404(Cart, user=self.request.user)
        total_amount = cart.total_amount + cart.total_tax_amount
        order = Order.objects.filter(user=self.request.user).order_by('-created_at')[0]
        order_items = OrderItem.objects.filter(cart=cart)
        order_items_list = []
        for item in order_items:
            d = {
                'product': str(item.product_inventory),
                'sku': item.product_inventory.sku,
                'quantity': item.quantity
            }
            order_items_list.append(d)
        order_items_json = json.dumps(order_items_list, indent=4)

        place_order = PlacedOrder.objects.create(
            user=self.request.user,
            order_items=order_items_json,
            total_amount=total_amount,
            order_number=order.order_number,
            order_date=order.created_at
        )
        place_order.save()

    def delete_cart_items(self):
        """Delete OrderItems from Cart and update Cart values."""
        OrderItem.objects.filter(cart__user=self.request.user).delete()
        cart = get_object_or_404(Cart, user=self.request.user)
        cart.quantity = 0
        cart.total_amount = 0
        cart.total_tax_amount = 0
        cart.save()

    def update_product_inventory_data(self):
        """Update ProductInventory data. Decrease value of units
           in stock of ProductInventory and increase units_sold."""
        order_items = OrderItem.objects.filter(cart__user=self.request.user)
        for item in order_items:
            stock = get_object_or_404(Stock, product_inventory=item.product_inventory)
            stock.units -= item.quantity
            stock.units_sold += item.quantity
            stock.save()

    def send_notification_email(self):
        order = Order.objects.filter(user=self.request.user).order_by('-created_at')[0]
        mail_subject = 'Your order was placed successfully!'
        mail_template = 'ecommerce/emails/order_notification.html'
        context = {
            'user': self.request.user,
            'order': order,
            'to_email': order.email,
        }
        send_notification(self.request, mail_subject, mail_template, context)

    def get(self, request, *args, **kwargs):
        self.create_placed_order()
        self.update_product_inventory_data()
        self.delete_cart_items()
        self.send_notification_email()
        return render(request, self.template_name)


class OrderHistoryView(LoginRequiredMixin, ListView):
    """view handles order history of logged-in user."""
    template_name = 'ecommerce/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        place_orders = PlacedOrder.objects.filter(user=self.request.user).order_by('-order_date')
        orders = []
        for order in place_orders:
            data = json.loads(order.order_items)
            d = {
                'order': order,
                'order_data': data
            }
            orders.append(d)
        return orders


class OrderHistoryDetailView(LoginRequiredMixin, TemplateView):
    """View displaying details of placed order."""
    template_name = 'ecommerce/detail_order_history.html'

    def get_products_inventories_data(self):
        order_number = self.kwargs.get('order_number')
        order_items_json = get_object_or_404(PlacedOrder, order_number=order_number).order_items
        order_items = json.loads(order_items_json)
        products_data = []
        for item in order_items:
            sku = item.get('sku')
            product_inventory = get_object_or_404(ProductInventory, sku=sku)
            image = Media.objects.filter(product_inventory=product_inventory, is_feature=True)
            if image:
                image = image[0]
            attribute_values = get_specific_attribute_values(product_inventory)
            data = {
                'product_inventory': product_inventory,
                'image': image,
                'quantity': item.get('quantity'),
                'attribute_values': attribute_values
            }
            products_data.append(data)
        return products_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products_data'] = self.get_products_inventories_data()
        order = get_object_or_404(Order, order_number=self.kwargs.get('order_number'))
        context['order'] = order
        return context
