from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import RedirectView, ListView

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
        names = room_name.split('__')
        if names[0] != request.user.username:
            other_user_name = names[0]
        else:
            other_user_name = names[1]
        context = {
            'room_name': room_name,
            'previous_messages': self.get_previous_messages(),
            'other_user_name': other_user_name
        }
        return render(request, self.template_name, context)


class UserMessagesView(LoginRequiredMixin, ListView):
    """View for sending all the conversations, so in this case
       ChatRooms with all needed data - usernames, last messages
       and room_names that are needed to get to the chat room."""
    template_name = 'chats/user_messages.html'
    context_object_name = 'chat_rooms'

    def get_queryset(self):
        if self.request.user.is_staff:
            chat_rooms = ChatRoom.objects.filter(
                Q(name__startswith=f'{self.request.user.username}__') |
                Q(name__endswith=f'__{self.request.user.username}') |
                Q(name__endswith='__support')).order_by('-date_created')
        else:
            chat_rooms = ChatRoom.objects.filter(
                Q(name__startswith=f'{self.request.user.username}__') |
                Q(name__endswith=f'__{self.request.user.username}')).order_by('-date_created')
        return chat_rooms

    def get_context_data(self, **kwargs):
        context = super(UserMessagesView, self).get_context_data(**kwargs)
        chat_rooms = self.get_queryset()
        names_and_last_messages = {}

        for room in chat_rooms:
            messages = Message.objects.filter(chat_room=room).order_by('-date_added')
            if messages:
                last_message = messages[0]
            else:
                last_message = 'No messages'
            names = room.name.split('__')
            if names[0] != self.request.user.username:
                names_and_last_messages.update({room.name: {names[0]: last_message}})
            else:
                names_and_last_messages.update({room.name: {names[1]: last_message}})

        context['names_and_last_messages'] = names_and_last_messages
        return context
