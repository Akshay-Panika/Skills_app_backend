from django.db import models
from user_auth.models import UserAuth
from service.models import Service


class ChatRoom(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="chat_rooms"
    )

    seller = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="seller_rooms"
    )

    buyer = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="buyer_rooms"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller_online = models.BooleanField(default=False)
    buyer_online = models.BooleanField(default=False)

    seller_typing = models.BooleanField(default=False)
    buyer_typing = models.BooleanField(default=False)

    class Meta:
        unique_together = ["service", "seller", "buyer"]

    def __str__(self):
        return f"Room #{self.id}"


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    message = models.TextField()

    is_delivered = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.message[:50]