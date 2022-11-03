from django.contrib import admin

from .models import Category, Product, ProductInventory, ProductType, ProductAttribute, \
    ProductAttributeValue, Stock, Brand, Media, ProductAttributeValues


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'is_active')
    list_filter = ('is_active', )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active', )


class ProductInventoryAdmin(admin.ModelAdmin):
    list_filter = ('is_active', 'product_type', 'is_on_sale')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductInventory, ProductInventoryAdmin)
admin.site.register(ProductType)
admin.site.register(Media)
admin.site.register(Stock)
admin.site.register(Brand)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductAttributeValues)
