from django.db import models
from user_auth.models import UserAuth
from service.models import Service


class ChatRoom(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='chat_rooms',
        null=True,     
        blank=True
    )
    buyer = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name='buyer_chats',
        null=True,     
        blank=True
    )
    seller = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name='seller_chats',
        null=True,     
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('service', 'buyer')

    def __str__(self):
        return f"Room({self.id}) | Service({self.service_id}) | Buyer({self.buyer_id}) | Seller({self.seller_id})"


class Message(models.Model):
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,     
        blank=True
    )
    sender = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True,     
        blank=True
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg({self.id}) from User({self.sender_id}) in Room({self.chat_room_id})"