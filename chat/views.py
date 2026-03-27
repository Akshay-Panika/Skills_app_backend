from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer


# ✅ Get messages (history)
class ChatMessagesView(APIView):
    def get(self, request, chat_room_id):
        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=404)

        messages = Message.objects.filter(
            chat_room=chat_room
        ).order_by("created_at")

        serializer = MessageSerializer(messages, many=True)

        return Response({
            "chat_room_id": chat_room.id,
            "messages": serializer.data
        })


# ✅ Inbox (chat list)
class UserChatsView(APIView):
    def get(self, request, user_id):
        chats = ChatRoom.objects.filter(
            Q(customer_id=user_id) | Q(provider_id=user_id)
        ).order_by("-created_at")

        serializer = ChatRoomSerializer(chats, many=True)

        return Response({
            "count": chats.count(),
            "data": serializer.data
        })