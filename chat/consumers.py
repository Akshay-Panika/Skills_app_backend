import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from user_auth.models import UserAuth
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f"chat_{self.room_id}"

        # Access check
        allowed = await self.check_access(self.room_id, self.user_id)
        if not allowed:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # ✅ Connect hone pe confirm bhejo
        await self.send(text_data=json.dumps({
            "type": "connected",
            "room_id": int(self.room_id),
            "user_id": int(self.user_id),
            "message": "Connected to chat room"
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            content = data.get("content", "").strip()

            if not content:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Empty message"
                }))
                return

            # DB mein save karo
            message_data = await self.save_message(
                self.room_id,
                self.user_id,
                content
            )

            if not message_data:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Message save failed"
                }))
                return

            # ✅ Room ke saare users ko broadcast karo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_id": message_data["id"],
                    "sender_id": message_data["sender"],
                    "content": message_data["content"],
                    "is_read": message_data["is_read"],
                    "created_at": str(message_data["created_at"]),
                    "sender_profile": message_data["sender_profile"],
                }
            )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON"
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def chat_message(self, event):
        """Group se aaya message sabko bhejo"""
        await self.send(text_data=json.dumps({
            "type": "message",
            "message_id": event["message_id"],
            "sender_id": event["sender_id"],
            "content": event["content"],
            "is_read": event["is_read"],
            "created_at": event["created_at"],
            "sender_profile": event["sender_profile"],
        }))

    @database_sync_to_async
    def check_access(self, room_id, user_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            user = UserAuth.objects.get(id=user_id)
            if not user.is_verified:
                return False
            return room.buyer_id == int(user_id) or room.seller_id == int(user_id)
        except (ChatRoom.DoesNotExist, UserAuth.DoesNotExist):
            return False

    @database_sync_to_async
    def save_message(self, room_id, user_id, content):
        try:
            room = ChatRoom.objects.get(id=room_id)
            user = UserAuth.objects.get(id=user_id)
            message = Message.objects.create(
                chat_room=room,
                sender=user,
                content=content
            )
            return MessageSerializer(message).data
        except Exception as e:
            print(f"Save message error: {e}")
            return None