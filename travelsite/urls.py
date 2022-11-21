"""travelsite URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from search.views import SearchProductInventory, CategoryList, ProductByCategory, ProductInventoryByWebId
from . import views
from search import views as search_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('', include('accounts.urls')),
    path('chat/', include('chats.urls')),
    path('shop/', include('ecommerce.urls')),

    # API / Search
    path('api/inventory/category/all/', CategoryList.as_view()),
    path(
        'api/inventory/products/category/<str:query>/',
        ProductByCategory.as_view(),
    ),
    path('api/inventory/<str:query>/', ProductInventoryByWebId.as_view()),
    path('api/search/<str:query>/', SearchProductInventory.as_view(), name='search-api'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
