from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ChatRoom(models.Model):
    """Model for a ChatRoom where users are connected to send Messages."""
    name = models.CharField(max_length=101, null=True, blank=True)
    users = models.ManyToManyField(User)
    data_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    """Model for messages that can be sent and created by users."""
    chat_room = models.ForeignKey(ChatRoom, related_name='chat_room', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        if len(self.content) > 10:
            return f'{self.user}: {self.content[10]}...'
        else:
            return f'{self.user}: {self.content}'

    class Meta:
        ordering = ('date_added',)
