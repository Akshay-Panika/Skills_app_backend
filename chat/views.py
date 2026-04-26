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
        try:
            service = Service.objects.get(id=request.data["service_id"])
            buyer = UserAuth.objects.get(id=request.data["buyer_id"])
            seller = service.user

            room, created = ChatRoom.objects.get_or_create(
                service=service,
                seller=seller,
                buyer=buyer
            )

            message_text = request.data.get("message", "")

            if message_text:
                ChatMessage.objects.create(
                    room=room,
                    sender=buyer,
                    message=message_text
                )

            payload = {
                "room_id": room.id,
                "service_id": service.id,
                "buyer_id": buyer.id,
                "seller_id": seller.id,
                "last_message": message_text,
                "updated_at": str(room.updated_at)
            }

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f"user_rooms_{seller.id}",
                {
                    "type": "room_created",
                    **payload
                }
            )

            async_to_sync(channel_layer.group_send)(
                f"user_rooms_{buyer.id}",
                {
                    "type": "room_created",
                    **payload
                }
            )

            return Response({
                "room_id": room.id,
                "created": created,
                "last_message": message_text
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
             
class ChatRoomListView(APIView):
    def get(self, request, user_id):
        rooms = ChatRoom.objects.filter(
            Q(buyer_id=user_id) | Q(seller_id=user_id)
        ).select_related(
            "service",
            "buyer",
            "seller"
        ).order_by("-updated_at")

        data = []

        for room in rooms:
            last_msg = room.messages.order_by(
                "-created_at"
            ).first()

            data.append({
                "room_id": room.id,

                # service full data
                "service": ServiceSerializer(
                    room.service
                ).data,

                # buyer info
                "buyer_id": room.buyer_id,
                "buyer_name": room.buyer.user_name,

                # seller info
                "seller_id": room.seller_id,
                "seller_name": room.seller.user_name,

                # last message
                "last_message":
                    last_msg.message if last_msg else "",

                # updated time
                "updated_at": room.updated_at
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
        try:
            room = ChatRoom.objects.filter(id=room_id).first()

            if not room:
                return Response({"error": "Room not found"}, status=404)

            seller_id = room.seller_id
            buyer_id = room.buyer_id

            room.delete()

            channel_layer = get_channel_layer()

            payload = {
                "room_id": room_id
            }

            async_to_sync(channel_layer.group_send)(
                f"user_rooms_{seller_id}",
                {
                    "type": "room_deleted",
                    **payload
                }
            )

            async_to_sync(channel_layer.group_send)(
                f"user_rooms_{buyer_id}",
                {
                    "type": "room_deleted",
                    **payload
                }
            )

            return Response({"message": "deleted"})

        except Exception as e:
            return Response({"error": str(e)}, status=500)