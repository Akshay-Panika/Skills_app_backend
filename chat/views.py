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

class CreateChatRoomView(APIView):
    def post(self, request):
        service_id = request.data.get("service_id")
        buyer_id = request.data.get("buyer_id")
        first_message = request.data.get("message", "").strip()

        if not service_id or not buyer_id:
            return Response({"error": "service_id and buyer_id required"}, status=400)

        service = get_object_or_404(Service, id=service_id)
        buyer = get_object_or_404(UserAuth, id=buyer_id)

        seller = service.user

        if seller.id == buyer.id:
            return Response({"error": "Seller cannot chat with self"}, status=400)

        try:
            with transaction.atomic():

                # 1️⃣ Create or get room
                room, created = ChatRoom.objects.get_or_create(
                    service=service,
                    seller=seller,
                    buyer=buyer,
                    defaults={"is_booked": True}
                )

                # 2️⃣ FORCE update service booking (IMPORTANT FIX)
                Service.objects.filter(id=service.id).update(is_booked=True)

                # 3️⃣ first message
                if first_message:
                    ChatMessage.objects.create(
                        room=room,
                        sender=buyer,
                        message=first_message
                    )

            return Response({
                "room_id": room.id,
                "created": created,
                "is_booked": True
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
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

                # 🔥 SERVICE INFO
                "service": ServiceSerializer(room.service).data,

                "buyer_id": room.buyer.id,
                "seller_id": room.seller.id,

                # 🔥 BOOKING STATUS
                "is_booked": room.is_booked,

                # 🔥 LAST MESSAGE
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
    

class DeleteChatRoomView(APIView):
    def delete(self, request, room_id):
        try:
            room = ChatRoom.objects.select_related("service").get(id=room_id)

            # 🔥 service ko unbook karo
            service = room.service
            service.is_booked = False
            service.save(update_fields=["is_booked"])

            # 🔥 room delete
            room.delete()

            return Response({
                "message": "Chat room deleted successfully",
                "is_booked": False
            }, status=200)

        except ChatRoom.DoesNotExist:
            return Response({
                "error": "Room not found"
            }, status=404)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=500)