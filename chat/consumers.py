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

        query = parse_qs(self.scope["query_string"].decode())
        user_id = query.get("user_id", [None])[0]

        self.user_id = int(user_id) if user_id else None

        room = await self.get_room()

        if not room:
            await self.close()
            return

        self.service_group = f"service_{room.service_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Optional service group
        await self.channel_layer.group_add(
            self.service_group,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connected",
            "message": "chat socket connected"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.service_group,
            self.channel_name
        )

    # =====================================================
    # VERY IMPORTANT → THIS WAS MISSING
    # This receives message from Flutter socket.sendMessage()
    # =====================================================
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            message = data.get("message")
            sender_id = data.get("sender")

            if not message or not sender_id:
                return

            # Save in database
            msg = await self.save_message(
                sender_id=sender_id,
                message=message
            )

            # Broadcast to all users in same room
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message",
                    "id": msg.id,
                    "room": self.room_id,
                    "sender": msg.sender_id,
                    "message": msg.message,
                    "is_seen": msg.is_seen,
                    "created_at": str(msg.created_at),
                }
            )

        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    # =====================================================
    # Send message to frontend
    # =====================================================
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "id": event["id"],
            "room": event["room"],
            "sender": event["sender"],
            "message": event["message"],
            "is_seen": event["is_seen"],
            "created_at": event["created_at"],
        }))

    async def room_created(self, event):
        await self.send(text_data=json.dumps(event))

    async def room_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_online_status(self, event):
        await self.send(text_data=json.dumps(event))

    # =====================================================
    # DB FUNCTIONS
    # =====================================================
    @sync_to_async
    def get_room(self):
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, sender_id, message):
        room = ChatRoom.objects.get(id=self.room_id)
        sender = UserAuth.objects.get(id=sender_id)

        msg = ChatMessage.objects.create(
            room=room,
            sender=sender,
            message=message
        )

        # update room updated_at
        room.save()

        return msg


# =========================================================
# ROOM LIST SOCKET
# =========================================================

class RoomListConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # ws/user/<user_id>/rooms/
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"user_rooms_{self.user_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connected",
            "message": "room list connected"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # New room created
    async def room_created(self, event):
        await self.send(text_data=json.dumps({
            "type": "room_created",
            "room_id": event["room_id"],
            "service_id": event["service_id"],
            "buyer_id": event["buyer_id"],
            "seller_id": event["seller_id"],
            "last_message": event["last_message"],
            "updated_at": event["updated_at"],
        }))

    # Room deleted
    async def room_deleted(self, event):
        await self.send(text_data=json.dumps({
            "type": "room_deleted",
            "room_id": event["room_id"]
        }))