from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
from service.models import Service
from service.serializers import ServiceSerializer
from user_auth.models import UserAuth
from django.db import transaction
from django.shortcuts import get_object_or_404

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class CreateChatRoomView(APIView):
    def post(self, request):
        service = Service.objects.get(id=request.data["service_id"])
        buyer = UserAuth.objects.get(id=request.data["buyer_id"])
        seller = service.user

        room, created = ChatRoom.objects.get_or_create(
            service=service,
            seller=seller,
            buyer=buyer
        )

        room.is_booked = True
        room.save()

        # 🔥 REALTIME PUSH TO BOTH USERS
        channel_layer = get_channel_layer()

        payload = {
            "type": "room_created",
            "room_id": room.id,
            "service_id": service.id,
            "buyer_id": buyer.id,
            "seller_id": seller.id,
            "is_booked": True
        }

        # 👉 Seller update
        async_to_sync(channel_layer.group_send)(
            f"user_rooms_{seller.id}",
            payload
        )

        # 👉 Buyer update
        async_to_sync(channel_layer.group_send)(
            f"user_rooms_{buyer.id}",
            payload
        )

        return Response({
            "room_id": room.id,
            "created": created
        })

class ChatRoomListView(APIView):
    def get(self, request, user_id):
        rooms = ChatRoom.objects.filter(
            Q(buyer_id=user_id) | Q(seller_id=user_id)
        ).select_related("service", "buyer", "seller").order_by("-updated_at")

        data = []

        for room in rooms:
            last_message = room.messages.last()

            data.append({
                "room_id": room.id,
                "service": ServiceSerializer(room.service).data,
                "buyer_id": room.buyer.id,
                "seller_id": room.seller.id,
                "is_booked": room.is_booked,
                "last_message": last_message.message if last_message else "",
                "updated_at": last_message.created_at if last_message else room.created_at
            })

        return Response(data)


class ChatHistoryView(APIView):
    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)

            messages = ChatMessage.objects.filter(room=room).order_by("created_at")

            serializer = ChatMessageSerializer(messages, many=True)

            return Response({
                "room_id": room.id,
                "messages": serializer.data
            })

        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)
        
class DeleteChatRoomView(APIView):
    def delete(self, request, room_id):
        room = ChatRoom.objects.get(id=room_id)

        seller_id = room.seller_id
        buyer_id = room.buyer_id

        room.delete()

        channel_layer = get_channel_layer()

        payload = {
            "type": "room_deleted",
            "room_id": room_id,
            "is_booked": False
        }

        async_to_sync(channel_layer.group_send)(
            f"user_rooms_{seller_id}",
            payload
        )

        async_to_sync(channel_layer.group_send)(
            f"user_rooms_{buyer_id}",
            payload
        )

        return Response({"message": "deleted"})
    