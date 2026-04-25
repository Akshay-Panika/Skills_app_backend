import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatRoom, ChatMessage
from user_auth.models import UserAuth



class ServiceChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
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

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add(self.service_group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(self.service_group, self.channel_name)


    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def room_created(self, event):
        await self.send(text_data=json.dumps(event))

    async def room_deleted(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_online_status(self, event):
        await self.send(text_data=json.dumps(event))


    @sync_to_async
    def get_room(self):
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None
        


class RoomListConsumer(AsyncWebsocketConsumer):

    async def connect(self):
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

    # 🔥 ROOM CREATED
    async def room_created(self, event):
        await self.send(text_data=json.dumps({
            "type": "room_created",
            "room": event["room"]
        }))

    # 🔥 ROOM DELETED
    async def room_deleted(self, event):
        await self.send(text_data=json.dumps({
            "type": "room_deleted",
            "room_id": event["room_id"]
        }))