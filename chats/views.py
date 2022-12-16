from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

from accounts.models import UserProfile
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


class RoomWithUserRedirectView(LoginRequiredMixin, RedirectView):
    """After attempting to chat with other user, this view gets or creates ChatRoom
       and redirects to it."""

    def get_or_create_chat_room(self):
        """Gets or creates ChatRoom according to the pattern -> username1__username2."""
        other_user_name = self.kwargs.get('chat_with')
        chat_room, created = ChatRoom.objects.get_or_create(
            Q(name=f'{self.request.user.username}__{other_user_name}') |
            Q(name=f'{other_user_name}__{self.request.user.username}')
        )
        if created:
            other_user = get_object_or_404(get_user_model(), username=other_user_name)
            chat_room.users.add(self.request.user, other_user)
        return chat_room

    def get_redirect_url(self, *args, **kwargs):
        chat_room = self.get_or_create_chat_room()
        return reverse('chat-room', args=[chat_room.name])


class ChatRoomsView(LoginRequiredMixin, TemplateView):
    """View gets all ChatRoom objects of logged-in user with all needed data."""
    template_name = 'chats/messages.html'

    def get_chat_rooms(self):
        """Returns user's ChatRoom objects based on pattern of
           ChatRoom names (name1__name2)."""
        if self.request.user.is_staff:
            chat_rooms = ChatRoom.objects.filter(
                Q(name__startswith=f'{self.request.user.username}__') |
                Q(name__endswith=f'__{self.request.user.username}') |
                Q(name__endswith='__support')).order_by('-date_created')
        else:
            chat_rooms = ChatRoom.objects.filter(
                Q(name__startswith=f'{self.request.user.username}__') |
                Q(name__endswith=f'__{self.request.user.username}'))
        return chat_rooms

    def get_last_messages(self):
        """Returns room names, names of users that chat is with,
           last messages of conversations, and users profiles.
           This data is needed to create a sidebar with all current
           conversations."""
        chat_rooms = self.get_chat_rooms()
        names_and_last_messages = []

        for room in chat_rooms:
            last_message = Message.objects.filter(chat_room=room).order_by('date_added').last()
            if not last_message:
                # the room is empty, there is no messages
                room.delete()
            else:
                names = room.name.split('__')
                if names[0] != self.request.user.username:
                    user_profile = get_object_or_404(UserProfile, user__username=names[0])
                    names_and_last_messages.append((room.name, names[0], last_message, user_profile))
                else:
                    user_profile = get_object_or_404(UserProfile, user__username=names[1])
                    names_and_last_messages.append((room.name, names[1], last_message, user_profile))

        # sorting list by last_message.date_added
        return sorted(names_and_last_messages, key=lambda element: element[2].date_added, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(** kwargs)
        if not self.get_chat_rooms():
            context['chats_exist'] = False
        else:
            context['chats_exist'] = True
            context['names_and_last_messages'] = self.get_last_messages()
        context['waiting_to_choose_chat'] = True
        return context


class ChatRoomWithUserMessages(UserPassesTestMixin, ChatRoomsView):
    """It extends the ChatRoomsView view so this view can do the same but also handle
       actual chatting and displaying previous messages."""

    def test_func(self):
        """Checks if the ChatRoom is theirs if not, raises PermissionDenied."""
        room_name = self.kwargs.get('room_name')
        users = room_name.split('__')
        if ((self.request.user.username in users) or
                ('support' in users and self.request.user.is_staff)):
            return True
        else:
            raise PermissionDenied

    def get_previous_messages(self):
        """Returns all messages of the given ChatRoom."""
        room_name = self.kwargs.get('room_name')
        chat_room = get_object_or_404(ChatRoom, name=room_name)
        messages = Message.objects.filter(chat_room=chat_room)
        return messages

    def get_context_data(self, **kwargs):
        context = super().get_context_data(** kwargs)
        room_name = self.kwargs.get('room_name')
        names = room_name.split('__')
        if names[0] != self.request.user.username:
            other_user_name = names[0]
        else:
            other_user_name = names[1]

        context['room_name'] = room_name
        context['previous_messages'] = self.get_previous_messages()
        context['other_user_name'] = other_user_name
        context['waiting_to_choose_chat'] = False
        return context
