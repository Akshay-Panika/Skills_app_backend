from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):

    user_image = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user", "user_phone"]

    def get_user_image(self, obj):
        if obj.user_image:
            return obj.user_image.url  
        return None