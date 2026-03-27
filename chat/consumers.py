import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatRoom, Message
from user_auth.models import UserAuth


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
        self.room_group_name = f"chat_{self.chat_room_id}"

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
        data = json.loads(text_data)

        message_text = data.get("message")
        sender_id = data.get("sender")

        sender = await self.get_user(sender_id)
        chat_room = await self.get_chat_room(self.chat_room_id)

        # 🔒 Security check
        is_valid = await self.is_valid_user(chat_room, sender)
        if not is_valid:
            return

        # ✅ Save message
        msg = await self.save_message(chat_room, sender, message_text)

        # 🔥 Broadcast
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg.message,
                "sender_id": sender.id,
                "created_at": str(msg.created_at),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # 🔽 DB helpers
    @sync_to_async
    def get_user(self, user_id):
        return UserAuth.objects.get(id=user_id)

    @sync_to_async
    def get_chat_room(self, chat_room_id):
        return ChatRoom.objects.get(id=chat_room_id)

    @sync_to_async
    def save_message(self, chat_room, sender, message):
        return Message.objects.create(
            chat_room=chat_room,
            sender=sender,
            message=message
        )

    @sync_to_async
    def is_valid_user(self, chat_room, sender):
        return sender.id in [chat_room.customer.id, chat_room.provider.id]