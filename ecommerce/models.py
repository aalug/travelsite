from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField

DATE_FORMAT = 'Y-m-d H:M:S'
MAX_PRICE = 'maximum price 999.99'
PRICE_RANGE_ERROR_MSG = 'the price must be between 0 and 999.99'


class Category(MPTTModel):
    """Category table implemented with MPTT."""
    name = models.CharField(max_length=100,
                            verbose_name=_('category name'),
                            help_text=_('format: required, max=100'))

    slug = models.SlugField(max_length=150,
                            verbose_name=_('category safe URL'),
                            help_text=_('format: required, letters, numbers, underscores or hyphens'))

    cover_photo = models.ImageField(upload_to='categories/cover_photos', blank=True, null=True)

    is_active = models.BooleanField(default=True)

    parent = TreeForeignKey('self', on_delete=models.PROTECT,
                            related_name='children',
                            null=True,
                            blank=True,
                            verbose_name='parent of category',
                            help_text=_('format: not required'))

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product details table."""
    web_id = models.CharField(max_length=50, unique=True,
                              verbose_name=_('product website ID'),
                              help_text=_('format: required, unique'))

    name = models.CharField(max_length=255, unique=False,
                            verbose_name=_('product name'),
                            help_text=_('format: required, max-255'))

    slug = models.SlugField(max_length=255, unique=False,
                            verbose_name=_('product safe URL'),
                            help_text=_('format: required, letters, numbers, underscores or hyphens'))

    description = models.TextField(unique=False,
                                   verbose_name=_('product description'),
                                   help_text=_('format: required'))

    category = TreeManyToManyField(Category)
    is_active = models.BooleanField(default=True,
                                    verbose_name=_('product visibility'),
                                    help_text=_('format: true=product visible'))

    created_at = models.DateTimeField(auto_now_add=True, editable=False,
                                      verbose_name=_('date product created'),
                                      help_text=_(f'format: {DATE_FORMAT}'))

    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('date product last update'),
                                      help_text=_(f'format: {DATE_FORMAT}'))

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Product brand table."""
    name = models.CharField(max_length=255, unique=True,
                            verbose_name=_('brand name'),
                            help_text=_('format: required, unique, max-255'))

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    """Product attribute table."""
    name = models.CharField(max_length=255, unique=True,
                            verbose_name=_('product attribute name'),
                            help_text=_('format: required, unique, max-255'))

    description = models.TextField(unique=False,
                                   verbose_name=_('product attribute description'),
                                   help_text=_('format: required'))

    def __str__(self):
        return self.name


class ProductType(models.Model):
    """Product type table."""
    name = models.CharField(max_length=255, unique=True,
                            verbose_name=_('type of product'),
                            help_text=_('format: required, unique, max-255'))

    product_type_attributes = models.ManyToManyField(ProductAttribute,
                                                     related_name='product_type_attributes',
                                                     through='ProductTypeAttribute')

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """Product attribute value table."""
    product_attribute = models.ForeignKey(ProductAttribute,
                                          related_name='product_attribute',
                                          on_delete=models.PROTECT)

    attribute_value = models.CharField(max_length=255, unique=False,
                                       verbose_name=_('attribute value'),
                                       help_text=_('format: required, max-255'))

    def __str__(self):
        return f'{self.product_attribute.name} : {self.attribute_value}'


class ProductInventory(models.Model):
    """Product inventory table."""
    sku = models.CharField(max_length=20, unique=True,
                           verbose_name=_('stock keeping unit'),
                           help_text=_('format: required, unique, max-20'))

    upc = models.CharField(max_length=12, unique=True,
                           verbose_name=_('universal product code'),
                           help_text=_('format: required, unique, max-12'))

    product_type = models.ForeignKey(ProductType, related_name='product_type', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='product', on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, related_name='brand', on_delete=models.PROTECT)

    attribute_values = models.ManyToManyField(ProductAttributeValue,
                                              related_name='product_attribute_values',
                                              through='ProductAttributeValues')

    is_active = models.BooleanField(default=True,
                                    verbose_name=_('product visibility'),
                                    help_text=_('format: true=product visible'))

    retail_price = models.DecimalField(max_digits=5, decimal_places=2, unique=False,
                                       verbose_name=_('recommended retail price'),
                                       help_text=_(f'format: {MAX_PRICE}'),
                                       error_messages={
                                           'name': {'max_length': _('{PRICE_RANGE_ERROR_MSG}.')}})

    store_price = models.DecimalField(max_digits=5, decimal_places=2, unique=False,
                                      verbose_name=_('regular store price'),
                                      help_text=_(f'format: {MAX_PRICE}'),
                                      error_messages={
                                          'name': {'max_length': _(f'{PRICE_RANGE_ERROR_MSG}.')}})

    sale_price = models.DecimalField(max_digits=5, decimal_places=2, unique=False,
                                     verbose_name=_('sale price'),
                                     help_text=_(f'format: {MAX_PRICE}'),
                                     error_messages={
                                         'name': {'max_length': _(f'{PRICE_RANGE_ERROR_MSG}.')}})

    is_on_sale = models.BooleanField(default=False,
                                     verbose_name=_('is the product on sale'),
                                     help_text=_('format: true=product is on sale'))

    weight = models.FloatField(unique=False, verbose_name=_('product weight'))

    created_at = models.DateTimeField(auto_now_add=True, editable=False,
                                      verbose_name=_('date sub-product created'),
                                      help_text=_(f'format: {DATE_FORMAT}'))

    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('date sub-product updated'),
                                      help_text=_(f'format: {DATE_FORMAT}'))

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _('product inventory')
        verbose_name_plural = _('product inventories')


class Media(models.Model):
    """The product image table."""
    product_inventory = models.ForeignKey(ProductInventory,
                                          on_delete=models.PROTECT,
                                          related_name='media_product_inventory')

    image = models.ImageField(unique=False,
                              verbose_name=_('product image'),
                              upload_to='products/',
                              help_text=_('format: required'))

    alt_text = models.CharField(max_length=255, unique=False,
                                verbose_name=_('alternative text'),
                                help_text=_('format: required, max-255'))

    is_feature = models.BooleanField(default=False,
                                     verbose_name=_('product default image'),
                                     help_text=_('format: default=false, true=default image'))

    created_at = models.DateTimeField(auto_now_add=True, editable=False,
                                      verbose_name=_('product visibility'),
                                      help_text=_(f'format: {DATE_FORMAT}'))

    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('date sub-product created'),
                                      help_text=_(f'format: {DATE_FORMAT}'))

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')


class Stock(models.Model):
    """Stock table."""
    product_inventory = models.OneToOneField(ProductInventory,
                                             related_name='product_inventory',
                                             on_delete=models.PROTECT)

    last_checked = models.DateTimeField(unique=False, null=True, blank=True,
                                        verbose_name=_('inventory stock check date'),
                                        help_text=_(f'format: {DATE_FORMAT}, null-true, blank-true'))

    units = models.IntegerField(default=0, unique=False,
                                verbose_name=_('units/qty of stock'),
                                help_text=_('format: required, default-0'))

    units_sold = models.IntegerField(default=0, unique=False,
                                     verbose_name=_('units sold to date'),
                                     help_text=_('format: required, default-0'))

    def __str__(self):
        return f'{self.product_inventory} | Stock'


class ProductAttributeValues(models.Model):
    """Product attribute values link table."""
    attributevalues = models.ForeignKey('ProductAttributeValue',
                                        related_name='attributevaluess',
                                        on_delete=models.PROTECT)

    productinventory = models.ForeignKey(ProductInventory,
                                         related_name='productattributevaluess',
                                         on_delete=models.PROTECT)

    def __str__(self):
        return str(self.attributevalues)

    class Meta:
        unique_together = (('attributevalues', 'productinventory'),)


class ProductTypeAttribute(models.Model):
    """Product type attributes link table."""
    product_attribute = models.ForeignKey(ProductAttribute,
                                          related_name='productattribute',
                                          on_delete=models.PROTECT)

    product_type = models.ForeignKey(ProductType,
                                     related_name='producttype',
                                     on_delete=models.PROTECT)

    category = models.ForeignKey(Category, null=True,
                                 related_name='category',
                                 on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.product_attribute}'

    class Meta:
        unique_together = (('product_attribute', 'product_type', 'category'),)


class Cart(models.Model):
    """Cart table."""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    total_amount = models.DecimalField(decimal_places=2, max_digits=6, default=Decimal(0))
    total_tax_amount = models.DecimalField(decimal_places=2, max_digits=6, default=Decimal(0))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s cart"


class OrderItem(models.Model):
    """Table for order items. It's a 'middleman' between
       ProductInventory and Cart. Thanks to this we can
       add to cart multiple of the same ProductInventory."""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    product_inventory = models.OneToOneField(ProductInventory, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    amount = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return f'{self.product_inventory}'


class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.PositiveIntegerField()
    product_type = models.ManyToManyField(ProductType)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'tax'

    def __str__(self):
        return self.tax_type


class Payment(models.Model):
    """Payment table."""
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('Other Method', 'Other Method'),
        ('Different Method', 'Different Method')
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    """Order table."""
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
    total = models.DecimalField(decimal_places=2, max_digits=6)
    total_tax = models.DecimalField(decimal_places=2, max_digits=6)
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.order_number


class PlacedOrder(models.Model):
    """Table for placed order - for storing history of orders."""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    order_items = models.JSONField(null=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=6)
    order_number = models.CharField(max_length=20)
    order_date = models.DateTimeField()

    def __str__(self):
        return f'Order: {self.order_number} ({self.user})'
