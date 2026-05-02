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
            last_msg = room.messages.order_by("-created_at").first()


            last_message = ""
            last_message_sender = None
            is_seen = True

            # ✅ APPLY LOGIC
            if last_msg:
                last_message = last_msg.message
                last_message_sender = last_msg.sender_id

                # 🔥 CORE LOGIC
                if last_msg.sender_id == user_id:
                    # mera message → check actual seen
                    is_seen = last_msg.is_seen
                else:
                    # dusre ka message → always seen
                    is_seen = True


            data.append({
                "room_id": room.id,

                "service": ServiceSerializer(room.service).data,

                "buyer_id": room.buyer_id,
                "buyer_name": (
                    room.buyer.profile.user_name
                    if hasattr(room.buyer, "profile")
                    and room.buyer.profile.user_name
                    else room.buyer.user_phone
                ),
                "buyer_image": (
                    room.buyer.profile.user_image.url
                    if hasattr(room.buyer, "profile")
                    and room.buyer.profile.user_image
                    else None
                ),

                "seller_id": room.seller_id,
                "seller_name": (
                    room.seller.profile.user_name
                    if hasattr(room.seller, "profile")
                    and room.seller.profile.user_name
                    else room.seller.user_phone
                ),
                "seller_image": (
                    room.seller.profile.user_image.url
                    if hasattr(room.seller, "profile")
                    and room.seller.profile.user_image
                    else None
                ),

                "last_message": last_message,
                "last_message_sender": last_message_sender,
                "is_seen": is_seen,

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
  
class BulkDeleteChatRoomView(APIView):
    def delete(self, request):
        try:
            room_ids = request.data.get("room_ids", [])

            if not room_ids:
                return Response(
                    {"error": "room_ids required"},
                    status=400
                )

            rooms = ChatRoom.objects.filter(id__in=room_ids)

            if not rooms.exists():
                return Response(
                    {"error": "Rooms not found"},
                    status=404
                )

            seller_ids = list(rooms.values_list("seller_id", flat=True))
            buyer_ids = list(rooms.values_list("buyer_id", flat=True))

            rooms.delete()

            channel_layer = get_channel_layer()

            payload = {"room_ids": room_ids}

            # notify all users
            for uid in set(seller_ids + buyer_ids):
                async_to_sync(channel_layer.group_send)(
                    f"user_rooms_{uid}",
                    {
                        "type": "room_deleted_bulk",
                        **payload
                    }
                )

            return Response({
                "message": "deleted",
                "deleted_ids": room_ids
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)