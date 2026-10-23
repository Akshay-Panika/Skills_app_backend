from rest_framework import serializers
from .models import UserAuth

class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuth
        fields = ["id", "user_phone", "is_verified", "created_at"]
        # fields = "__all__"

class OTPVerifySerializer(serializers.Serializer):
    user_phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)