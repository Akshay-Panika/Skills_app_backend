from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
from service.models import Service
from service.serializers import ServiceSerializer
from user_auth.models import UserAuth


# ================= CREATE ROOM =================
class CreateChatRoomView(APIView):
    def post(self, request):
        service_id = request.data.get("service_id")
        buyer_id = request.data.get("buyer_id")
        first_message = request.data.get("message", "")

        if not service_id or not buyer_id:
            return Response({"error": "service_id and buyer_id required"}, status=400)

        try:
            service = Service.objects.select_related("user").get(id=service_id)
            buyer = UserAuth.objects.get(id=buyer_id)
        except:
            return Response({"error": "Invalid data"}, status=404)

        seller = service.user

        if seller.id == buyer.id:
            return Response({"error": "Seller cannot chat with self"}, status=400)

        room, created = ChatRoom.objects.get_or_create(
            service=service,
            seller=seller,
            buyer=buyer
        )

        if created and first_message.strip():
            ChatMessage.objects.create(
                room=room,
                sender=buyer,
                message=first_message
            )

        return Response({
            "room_id": room.id,
            "service": ServiceSerializer(service).data,
            "seller_id": seller.id,
            "buyer_id": buyer.id,
            "created": created
        })


# ================= ROOM LIST =================
class ChatRoomListView(APIView):
    def get(self, request, user_id):

        rooms = ChatRoom.objects.filter(
            Q(buyer_id=user_id) | Q(seller_id=user_id)
        ).select_related("service", "buyer", "seller").order_by("-created_at")

        data = []

        for room in rooms:
            last_msg = room.messages.last()

            data.append({
                "room_id": room.id,
                "service": ServiceSerializer(room.service).data,

                "buyer_id": room.buyer.id,
                "seller_id": room.seller.id,

                "online": {
                    "buyer": room.buyer_online,
                    "seller": room.seller_online
                },

                "typing": {
                    "buyer": room.buyer_typing,
                    "seller": room.seller_typing
                },

                "last_message": last_msg.message if last_msg else None,
                "last_time": last_msg.created_at if last_msg else room.created_at,

                "unread_count": room.messages.filter(is_seen=False).count()
            })

        return Response(data)


# ================= CHAT HISTORY =================
class ChatHistoryView(APIView):
    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
        except:
            return Response({"error": "Room not found"}, status=404)

        messages = room.messages.order_by("created_at")

        return Response({
            "room_id": room.id,
            "messages": ChatMessageSerializer(messages, many=True).data
        })