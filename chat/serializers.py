from rest_framework import serializers
from .models import ChatRoom, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_phone = serializers.CharField(source="sender.user_phone", read_only=True)

    class Meta:
        model = Message
        fields = "__all__"


class ChatRoomSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.service_name", read_only=True)
    customer_phone = serializers.CharField(source="customer.user_phone", read_only=True)
    provider_phone = serializers.CharField(source="provider.user_phone", read_only=True)

    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = "__all__"

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        return last.message if last else None