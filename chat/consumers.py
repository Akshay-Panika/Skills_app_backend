# chat/consumers.py (FULL UPDATED FIXED CODE)

import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import ChatRoom, ChatMessage
from user_auth.models import UserAuth


class ServiceChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # ws/chat/<room_id>/
        self.room_id = int(
            self.scope["url_route"]["kwargs"]["room_id"]
        )

        self.group_name = f"chat_{self.room_id}"

        query = parse_qs(
            self.scope["query_string"].decode()
        )

        user_id = query.get("user_id", [None])[0]

        if not user_id:
            await self.close()
            return

        self.user_id = int(user_id)

        room = await self.get_room()

        if not room:
            await self.close()
            return

        self.service_group = f"service_{room.service_id}"

        # join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # optional service group
        await self.channel_layer.group_add(
            self.service_group,
            self.channel_name
        )

        await self.accept()

        # online status broadcast
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "user_online_status",
                "user_id": self.user_id,
                "is_online": True,
            }
        )

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

        # offline status broadcast
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "user_online_status",
                "user_id": self.user_id,
                "is_online": False,
            }
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get("type")

            # ====================================
            # CHAT MESSAGE
            # ====================================
            if event_type == "chat_message":
                message = data.get("message")
                sender_id = data.get("sender")

                if not message or not sender_id:
                    return

                sender_id = int(sender_id)

                msg = await self.save_message(
                    sender_id=sender_id,
                    message=message
                )

                # IMPORTANT FIX:
                # room must be int not string
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat_message",
                        "id": int(msg.id),
                        "room": int(self.room_id),
                        "sender": int(msg.sender_id),
                        "message": str(msg.message),
                        "is_seen": bool(msg.is_seen),
                        "created_at": str(msg.created_at),
                    }
                )

            # ====================================
            # TYPING STATUS
            # ====================================
            elif event_type == "typing":
                # Flutter sends: typing
                is_typing = data.get("typing", False)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat_typing",
                        "user_id": int(self.user_id),
                        "is_typing": bool(is_typing),
                    }
                )

            # ====================================
            # ONLINE STATUS
            # ====================================
            elif event_type == "online_status":
                is_online = data.get("is_online", False)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "user_online_status",
                        "user_id": int(self.user_id),
                        "is_online": bool(is_online),
                    }
                )

        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    # ====================================
    # SEND TO FLUTTER
    # ====================================

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "id": int(event["id"]),
            "room": int(event["room"]),
            "sender": int(event["sender"]),
            "message": str(event["message"]),
            "is_seen": bool(event["is_seen"]),
            "created_at": str(event["created_at"]),
        }))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": int(event["user_id"]),
            "is_typing": bool(event["is_typing"]),
        }))

    async def user_online_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "online_status",
            "user_id": int(event["user_id"]),
            "is_online": bool(event["is_online"]),
        }))

    async def room_created(self, event):
        await self.send(text_data=json.dumps(event))

    async def room_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    # ====================================
    # DATABASE FUNCTIONS
    # ====================================

    @sync_to_async
    def get_room(self):
        try:
            return ChatRoom.objects.get(
                id=self.room_id
            )
        except ChatRoom.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, sender_id, message):
        room = ChatRoom.objects.get(
            id=self.room_id
        )

        sender = UserAuth.objects.get(
            id=sender_id
        )

        msg = ChatMessage.objects.create(
            room=room,
            sender=sender,
            message=message
        )

        # update room updated_at
        room.save()

        return msg


# =====================================================
# ROOM LIST SOCKET
# =====================================================

class RoomListConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = int(
            self.scope["url_route"]["kwargs"]["user_id"]
        )

        self.group_name = (
            f"user_rooms_{self.user_id}"
        )

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

    async def room_created(self, event):
        await self.send(text_data=json.dumps({
            "type": "room_created",
            "room_id": int(event["room_id"]),
            "service_id": int(event["service_id"]),
            "buyer_id": int(event["buyer_id"]),
            "seller_id": int(event["seller_id"]),
            "last_message": str(event["last_message"]),
            "updated_at": str(event["updated_at"]),
        }))

    async def room_deleted(self, event):
        await self.send(text_data=json.dumps({
            "type": "room_deleted",
            "room_id": int(event["room_id"]),
        }))