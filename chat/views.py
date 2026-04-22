from rest_framework.views import APIView
from rest_framework.response import Response
from user_auth.models import UserAuth
from service.models import Service
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer


def get_user(user_id):
    try:
        user = UserAuth.objects.get(id=user_id)
        if not user.is_verified:
            return None, "User is not verified"
        return user, None
    except UserAuth.DoesNotExist:
        return None, "User not found"


class RequestServiceChatView(APIView):
    """Service ke liye chat room banao ya existing return karo"""

    def post(self, request, service_id):
        buyer_id = request.data.get("user_id")

        if not buyer_id:
            return Response({"error": "user_id is required"}, status=400)

        buyer, error = get_user(buyer_id)
        if error:
            return Response({"error": error}, status=400)

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)

        if service.user == buyer:
            return Response(
                {"error": "Apni service ke liye request nahi kar sakte"},
                status=400
            )

        chat_room, created = ChatRoom.objects.get_or_create(
            service=service,
            buyer=buyer,
            defaults={"seller": service.user}
        )

        serializer = ChatRoomSerializer(
            chat_room,
            context={"user_id": int(buyer_id)}
        )

        return Response({
            "created": created,
            "chat_room": serializer.data
        }, status=201 if created else 200)


class UserChatListView(APIView):
    """User ki saari chat rooms - buyer + seller dono"""

    def get(self, request, user_id):
        user, error = get_user(user_id)
        if error:
            return Response({"error": error}, status=400)

        room_ids = list(
            ChatRoom.objects.filter(buyer=user).values_list('id', flat=True)
        ) + list(
            ChatRoom.objects.filter(seller=user).values_list('id', flat=True)
        )

        rooms = ChatRoom.objects.filter(
            id__in=room_ids
        ).select_related(
            'service',
            'buyer__profile',
            'seller__profile'
        ).order_by('-id')

        serializer = ChatRoomSerializer(
            rooms,
            many=True,
            context={"user_id": int(user_id)}
        )

        return Response({
            "count": rooms.count(),
            "chat_rooms": serializer.data
        })


class ChatRoomDetailView(APIView):
    """Ek room ki detail"""

    def get(self, request, room_id):
        user_id = request.GET.get("user_id")

        try:
            room = ChatRoom.objects.select_related(
                'service',
                'buyer__profile',
                'seller__profile'
            ).get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=404)

        if str(room.buyer_id) != str(user_id) and str(room.seller_id) != str(user_id):
            return Response({"error": "Access denied"}, status=403)

        serializer = ChatRoomSerializer(
            room,
            context={"user_id": int(user_id) if user_id else None}
        )
        return Response(serializer.data)


class ChatMessageListView(APIView):
    """Room ke saare messages fetch karo + read mark karo"""

    def get(self, request, room_id):
        user_id = request.GET.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=404)

        if str(room.buyer_id) != str(user_id) and str(room.seller_id) != str(user_id):
            return Response({"error": "Access denied"}, status=403)

        # Doosre ki unread messages read mark karo
        room.messages.filter(
            is_read=False
        ).exclude(sender_id=user_id).update(is_read=True)

        messages = room.messages.select_related(
            'sender__profile'
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True)

        return Response({
            "count": messages.count(),
            "messages": serializer.data
        })


class SendMessageView(APIView):
    """REST se message bhejo (WebSocket backup)"""

    def post(self, request, room_id):
        user_id = request.data.get("user_id")
        content = request.data.get("content", "").strip()

        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        if not content:
            return Response({"error": "Message content is required"}, status=400)

        user, error = get_user(user_id)
        if error:
            return Response({"error": error}, status=400)

        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Chat room not found"}, status=404)

        if room.buyer != user and room.seller != user:
            return Response({"error": "Access denied"}, status=403)

        message = Message.objects.create(
            chat_room=room,
            sender=user,
            content=content
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=201)