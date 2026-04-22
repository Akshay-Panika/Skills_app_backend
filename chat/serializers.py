from rest_framework import serializers
from .models import ChatRoom, Message
from user_profile.serializers import UserProfileSerializer
from service.serializers import ServiceSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_profile = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'chat_room', 'sender', 'sender_profile',
            'content', 'is_read', 'created_at'
        ]
        read_only_fields = ['sender', 'chat_room', 'created_at']

    def get_sender_profile(self, obj):
        if hasattr(obj.sender, 'profile'):
            return UserProfileSerializer(obj.sender.profile).data
        return None


class ChatRoomSerializer(serializers.ModelSerializer):
    service_detail = serializers.SerializerMethodField()
    buyer_profile = serializers.SerializerMethodField()
    seller_profile = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'service', 'service_detail',
            'buyer', 'buyer_profile',
            'seller', 'seller_profile',
            'last_message', 'unread_count', 'created_at'
        ]

    def get_service_detail(self, obj):
        return ServiceSerializer(obj.service).data

    def get_buyer_profile(self, obj):
        if hasattr(obj.buyer, 'profile'):
            return UserProfileSerializer(obj.buyer.profile).data
        return None

    def get_seller_profile(self, obj):
        if hasattr(obj.seller, 'profile'):
            return UserProfileSerializer(obj.seller.profile).data
        return None

    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        if last:
            return {
                'content': last.content,
                'created_at': last.created_at,
                'sender_id': last.sender_id
            }
        return None

    def get_unread_count(self, obj):
        user_id = self.context.get('user_id')
        if user_id:
            return obj.messages.filter(
                is_read=False
            ).exclude(sender_id=user_id).count()
        return 0