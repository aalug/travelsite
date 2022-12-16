from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='user-messages', permanent=True)),
    path('my-messages/', views.ChatRoomsView.as_view(), name='user-messages'),
    path('chat-with-support/<str:room_name>/', views.RoomWithSupportRedirectView.as_view(), name='chat-with-support'),
    path('chat-with-user/<str:chat_with>/', views.RoomWithUserRedirectView.as_view(), name='chat-with-user'),
    path('<str:room_name>/', views.ChatRoomWithUserMessages.as_view(), name='chat-room')
]

