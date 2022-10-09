import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from chats.models import ChatRoom, Message

User = get_user_model()


class ChatRoomConsumer(AsyncWebsocketConsumer):
    """Consumer for chat rooms."""

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        room_name = text_data_json['room_name']

        await self.save_message(username, room_name, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': username
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, username, room_name, message):
        params = {
            'user': User.objects.get(username=username),
            'chat_room': ChatRoom.objects.get(name=room_name),
            'content': message
        }
        Message.objects.create(**params)


        # biorę <str:name>, robię '-'.split()
        # mam dwóch userów, jezeli jest support to kazdy is_staff moze sie zalogowac

        # room tworzy się w momencie wejscia w nowy url


