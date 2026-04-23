import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import ChatRoom, ChatMessage
from user_auth.models import UserAuth


class ServiceChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

        # ✅ SAFE QUERY PARSE (FIXED)
        query_params = parse_qs(self.scope["query_string"].decode())
        user_id = query_params.get("user_id", [None])[0]

        self.user_id = int(user_id) if user_id else None

        self.group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        if self.user_id:
            await self.set_online(True)

    async def disconnect(self, close_code):
        if self.user_id:
            await self.set_online(False)

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "message":
            msg = await self.save_message(
                data["sender_id"],
                data["message"]
            )

            # ✅ FIXED EVENT FORMAT
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message",
                    "message": data["message"],
                    "sender_id": data["sender_id"],
                    "message_id": msg.id
                }
            )

        elif event_type == "typing":
            await self.set_typing(data["sender_id"], data["typing"])

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_typing",
                    "sender_id": data["sender_id"],
                    "typing": data["typing"]
                }
            )

    # ================= EVENTS =================

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    # ================= DB =================

    @sync_to_async
    def save_message(self, sender_id, message):
        room = ChatRoom.objects.get(id=self.room_id)
        sender = UserAuth.objects.get(id=sender_id)

        return ChatMessage.objects.create(
            room=room,
            sender=sender,
            message=message
        )

    @sync_to_async
    def set_online(self, status):
        try:
            room = ChatRoom.objects.get(id=self.room_id)

            if self.user_id == room.buyer_id:
                room.buyer_online = status
            elif self.user_id == room.seller_id:
                room.seller_online = status

            room.save()
        except:
            pass

    @sync_to_async
    def set_typing(self, sender_id, typing):
        try:
            room = ChatRoom.objects.get(id=self.room_id)

            if sender_id == room.buyer_id:
                room.buyer_typing = typing
            elif sender_id == room.seller_id:
                room.seller_typing = typing

            room.save()
        except:
            pass