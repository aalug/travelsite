from django.urls import path
from . import views
urlpatterns = [
    path('', views.MainForumPageView.as_view(), name='forum'),
    path('category/<slug:slug>/', views.PostsByCategoryView.as_view(), name='posts-by-category'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('add-comment/', views.AddCommentView.as_view(), name='add-comment'),
    path('add-reply/', views.AddReplyView.as_view(), name='add-reply'),
]

