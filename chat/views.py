# chat/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
from service.models import Service
from service.serializers import ServiceSerializer
from user_auth.models import UserAuth
from django.db.models import Q


class CreateChatRoomView(APIView):
    def post(self, request):
        service_id = request.data.get("service_id")
        buyer_id = request.data.get("buyer_id")
        first_message = request.data.get("message", "")

        if not service_id or not buyer_id:
            return Response({
                "error": "service_id and buyer_id required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.select_related(
                "user",
                "user__profile",
                "category",
                "subcategory"
            ).get(id=service_id)

            buyer = UserAuth.objects.get(id=buyer_id)

        except Service.DoesNotExist:
            return Response({
                "error": "Service not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except UserAuth.DoesNotExist:
            return Response({
                "error": "Buyer not found"
            }, status=status.HTTP_404_NOT_FOUND)

        seller = service.user

        # seller khud se chat nahi kar sakta
        if seller.id == buyer.id:
            return Response({
                "error": "Seller cannot chat with self"
            }, status=status.HTTP_400_BAD_REQUEST)

        # room create ya existing room fetch
        room, created = ChatRoom.objects.get_or_create(
            service=service,
            seller=seller,
            buyer=buyer
        )

        # agar naya room bana aur message bheja gaya ho
        if created and first_message.strip():
            ChatMessage.objects.create(
                room=room,
                sender=buyer,
                message=first_message.strip()
            )

        # full service serializer
        service_data = ServiceSerializer(service).data

        return Response({
            "room_id": room.id,
            "service": service_data,   # 🔥 full service model parse
            "seller_id": seller.id,
            "buyer_id": buyer.id,
            "created": created
        }, status=status.HTTP_200_OK)

class ChatRoomListView(APIView):
    def get(self, request, user_id):

        rooms = ChatRoom.objects.filter(
            Q(buyer_id=user_id) |
            Q(seller_id=user_id)
        ).select_related("service", "buyer", "seller")

        data = []

        for room in rooms:
            last_msg = ChatMessage.objects.filter(room=room).last()

            data.append({
                "room_id": room.id,
                "service": ServiceSerializer(room.service).data,
                "buyer_id": room.buyer.id,
                "seller_id": room.seller.id,
                "last_message": last_msg.message if last_msg else None,
                "updated_at": last_msg.created_at if last_msg else room.created_at
            })

        return Response(data)

class ChatHistoryView(APIView):
    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)

        except ChatRoom.DoesNotExist:
            return Response({
                "error": "Room not found"
            }, status=status.HTTP_404_NOT_FOUND)

        messages = ChatMessage.objects.filter(
            room=room
        ).order_by("created_at")

        serializer = ChatMessageSerializer(
            messages,
            many=True
        )

        return Response({
            "room_id": room.id,
            "messages": serializer.data
        })