from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainShopPageView.as_view(), name='shop'),
    path('categories/<slug:slug>/', views.ProductsByCategoryView.as_view(), name='products-by-category'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-details'),
    path('search/', views.SearchProductInventoryView.as_view(), name='search'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('delete-order-item/<str:sku>/', views.DeleteOrderItemView.as_view(), name='delete-order-item'),
    path('delete-cart/', views.DeleteCartView.as_view(), name='delete-cart'),
    path('order/', views.OrderConfirmationView.as_view(), name='order'),
    path('checkout/', views.CheckOutView.as_view(), name='checkout'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('order-placed-succesfully/', views.OrderPlacedView.as_view(), name='order-placed'),
    path('order-history/', views.OrderHistoryView.as_view(), name='order-history'),
    path('detail-order-history/<str:order_number>/', views.OrderHistoryDetailView.as_view(),
         name='detail-order-history')
]
