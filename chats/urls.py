from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='home', permanent=True)),
    path('my-messages/', views.UserMessagesView.as_view(), name='user-messages'),
    path('chat-with-support/<str:room_name>/', views.RoomWithSupportRedirectView.as_view(), name='chat-with-support'),
    path('<str:room_name>/', views.ChatRoomView.as_view(), name='chat-room'),
]

