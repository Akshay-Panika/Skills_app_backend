from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
from service.models import Service
from service.serializers import ServiceSerializer
from user_auth.models import UserAuth


class CreateChatRoomView(APIView):
    def post(self, request):
        service_id = request.data.get("service_id")
        buyer_id = request.data.get("buyer_id")
        first_message = request.data.get("message", "").strip()

        if not service_id or not buyer_id:
            return Response({
                "error": "service_id and buyer_id required"
            }, status=400)

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
            }, status=404)

        except UserAuth.DoesNotExist:
            return Response({
                "error": "Buyer not found"
            }, status=404)

        seller = service.user

        if seller.id == buyer.id:
            return Response({
                "error": "Seller cannot chat with self"
            }, status=400)

        room, created = ChatRoom.objects.get_or_create(
            service=service,
            seller=seller,
            buyer=buyer
        )

        # IMPORTANT FIX
        # room old ho ya new
        # message ALWAYS save hoga

        if first_message:
            ChatMessage.objects.create(
                room=room,
                sender=buyer,
                message=first_message
            )

        return Response({
            "room_id": room.id,
            "created": created,
            "seller_id": seller.id,
            "buyer_id": buyer.id,
            "service": ServiceSerializer(service).data
        })


class ChatRoomListView(APIView):
    def get(self, request, user_id):
        rooms = ChatRoom.objects.filter(
            Q(buyer_id=user_id) |
            Q(seller_id=user_id)
        ).select_related(
            "service",
            "buyer",
            "seller"
        ).order_by("-updated_at")

        data = []

        for room in rooms:
            last_message = room.messages.last()

            data.append({
                "room_id": room.id,
                "service": ServiceSerializer(room.service).data,
                "buyer_id": room.buyer.id,
                "seller_id": room.seller.id,
                "last_message": last_message.message if last_message else "",
                "updated_at": last_message.created_at if last_message else room.created_at
            })

        return Response(data)


class ChatHistoryView(APIView):
    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)

        except ChatRoom.DoesNotExist:
            return Response({
                "error": "Room not found"
            }, status=404)

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