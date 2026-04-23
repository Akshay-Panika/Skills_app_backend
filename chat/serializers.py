from rest_framework import serializers
from .models import ChatRoom, ChatMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.user_phone", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "room",
            "sender",
            "sender_name",
            "message",
            "is_seen",
            "is_delivered",
            "created_at"
        ]