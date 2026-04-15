from rest_framework import serializers
from .models import Service
from user_profile.serializers import UserProfileSerializer


class ServiceSerializer(serializers.ModelSerializer):
    service_image = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Service
        exclude = ["user"]

    # 🔥 FIX IMAGE URL
    def get_service_image(self, obj):
        if obj.service_image:
            return obj.service_image.url
        return ""

    def get_user_profile(self, obj):
        if hasattr(obj.user, "profile"):
            return UserProfileSerializer(obj.user.profile).data
        return None

    def get_is_favorite(self, obj):
        favorite_ids = self.context.get("favorite_ids", [])
        return obj.id in favorite_ids

    def get_distance(self, obj):
        distance = getattr(obj, "distance", None)

        if distance is None:
            return None

        if distance < 0.05:
            return "Nearby"

        if distance < 1:
            return f"{round(distance * 1000)} m"

        return f"{round(distance, 2)} km"