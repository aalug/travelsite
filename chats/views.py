from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import RedirectView, TemplateView

from chats.models import ChatRoom, Message


class RoomWithSupportRedirectView(LoginRequiredMixin, RedirectView):
    """view that, if the user is logged-in, creates the ChatRoom model
       and redirects the user to an appropriate url."""

    def get_or_create_chat_room(self):
        """Method for getting the chat room if it was created before,
           or creating it and assigning logged-in user and all staff
           members to it so that every one of them can answer. """
        try:
            chat_room = ChatRoom.objects.get(name=f'{self.request.user.username}__support')
        except ChatRoom.DoesNotExist:
            chat_room = ChatRoom.objects.create(name=f'{self.request.user.username}__support')
            chat_room.save()
            chat_room.users.add(self.request.user)
            staff_members = get_user_model().objects.filter(is_staff=True)
            chat_room.users.add(*staff_members)

        return chat_room

    def get_redirect_url(self, *args, **kwargs):
        chat_room = self.get_or_create_chat_room()
        url = reverse('chat-room', args=[chat_room.name])
        return url


class ChatRoomView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Chat room view. To enter user has to be authenticated and pass
       the test - be on of the users associated with this particular ChatRoom"""
    template_name = 'chats/chat_room.html'

    def test_func(self):
        room_name = self.kwargs.get('room_name')
        users = room_name.split('__')
        if self.request.user.username in users:
            return True
        elif 'support' in users and self.request.user.is_staff:
            return True
        else:
            raise PermissionDenied

    def get_previous_messages(self):
        room_name = self.kwargs.get('room_name')
        chat_room = ChatRoom.objects.get(name=room_name)
        messages = Message.objects.filter(chat_room=chat_room)
        return messages

    def get(self, request, room_name):
        context = {
            'room_name': room_name,
            'previous_messages': self.get_previous_messages()
        }
        return render(request, self.template_name, context)

