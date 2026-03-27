from django.db import models
from user_auth.models import UserAuth
from service.models import Service


class ChatRoom(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.ForeignKey(UserAuth, on_delete=models.CASCADE, related_name="customer_chats")
    provider = models.ForeignKey(UserAuth, on_delete=models.CASCADE, related_name="provider_chats")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['service', 'customer', 'provider']


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:20]