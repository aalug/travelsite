from django.urls import path
from . import views
urlpatterns = [
    path('', views.MainShopPageView.as_view(), name='shop'),
    path('create/', views.CategoriesListView.as_view()),
    path('categories/<slug:slug>/', views.ProductsByCategoryView.as_view(), name='products-by-category'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-details'),
]

