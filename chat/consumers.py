# chat/consumers.py

import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import ChatRoom, ChatMessage
from user_auth.models import UserAuth


class ServiceChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # ws/chat/<room_id>/
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"chat_{self.room_id}"

        # query string se user_id
        # ws://.../ws/chat/5/?user_id=2
        query_params = parse_qs(
            self.scope["query_string"].decode()
        )

        user_id = query_params.get("user_id", [None])[0]
        self.user_id = int(user_id) if user_id else None

        # room exist check
        room_exists = await self.check_room_exists()

        if not room_exists:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # online status update
        if self.user_id:
            await self.set_online_status(True)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "user_online_status",
                    "user_id": self.user_id,
                    "is_online": True
                }
            )

    async def disconnect(self, close_code):
        if self.user_id:
            await self.set_online_status(False)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "user_online_status",
                    "user_id": self.user_id,
                    "is_online": False
                }
            )

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Expected payloads:

        Message:
        {
            "type": "message",
            "sender_id": 2,
            "message": "Hello bro"
        }

        Typing:
        {
            "type": "typing",
            "sender_id": 2,
            "typing": true
        }

        Seen:
        {
            "type": "seen",
            "message_id": 15
        }
        """

        data = json.loads(text_data)
        event_type = data.get("type")

        # =========================
        # SEND MESSAGE
        # =========================

        if event_type == "message":
            sender_id = data.get("sender_id")
            message = data.get("message", "").strip()

            if not sender_id or not message:
                return

            saved_message = await self.save_message(
                sender_id,
                message
            )

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message",
                    "message_id": saved_message.id,
                    "sender_id": sender_id,
                    "message": message,
                    "created_at": str(saved_message.created_at),
                    "is_seen": False,
                    "is_delivered": True
                }
            )

        # =========================
        # TYPING STATUS
        # =========================

        elif event_type == "typing":
            sender_id = data.get("sender_id")
            typing = data.get("typing", False)

            if not sender_id:
                return

            await self.set_typing_status(
                sender_id,
                typing
            )

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_typing",
                    "sender_id": sender_id,
                    "typing": typing
                }
            )

        # =========================
        # MESSAGE SEEN
        # =========================

        elif event_type == "seen":
            message_id = data.get("message_id")

            if not message_id:
                return

            await self.mark_message_seen(message_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "message_seen",
                    "message_id": message_id,
                    "is_seen": True
                }
            )

    # =====================================================
    # SOCKET EVENTS → SEND TO FLUTTER
    # =====================================================

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_seen(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_online_status(self, event):
        await self.send(text_data=json.dumps(event))

    # =====================================================
    # DATABASE METHODS
    # =====================================================

    @sync_to_async
    def check_room_exists(self):
        return ChatRoom.objects.filter(
            id=self.room_id
        ).exists()

    @sync_to_async
    def save_message(self, sender_id, message):
        room = ChatRoom.objects.get(
            id=self.room_id
        )

        sender = UserAuth.objects.get(
            id=sender_id
        )

        return ChatMessage.objects.create(
            room=room,
            sender=sender,
            message=message,
            is_delivered=True
        )

    @sync_to_async
    def set_online_status(self, status):
        try:
            room = ChatRoom.objects.get(
                id=self.room_id
            )

            if self.user_id == room.buyer_id:
                room.buyer_online = status

            elif self.user_id == room.seller_id:
                room.seller_online = status

            room.save()

        except Exception:
            pass

    @sync_to_async
    def set_typing_status(self, sender_id, typing):
        try:
            room = ChatRoom.objects.get(
                id=self.room_id
            )

            if sender_id == room.buyer_id:
                room.buyer_typing = typing

            elif sender_id == room.seller_id:
                room.seller_typing = typing

            room.save()

        except Exception:
            pass

    @sync_to_async
    def mark_message_seen(self, message_id):
        try:
            msg = ChatMessage.objects.get(
                id=message_id
            )

            msg.is_seen = True
            msg.save()

        except Exception:
            pass