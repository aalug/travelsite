from django.urls import path
from . import views
urlpatterns = [
    path('', views.MainForumPageView.as_view(), name='forum'),
    path('category/<slug:slug>/', views.PostsByCategoryView.as_view(), name='posts-by-category'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
]

