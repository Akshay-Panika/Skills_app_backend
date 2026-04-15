from rest_framework import serializers
from .models import Service
from user_profile.serializers import UserProfileSerializer


class ServiceSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Service
        exclude = ["user"]

    def get_user_profile(self, obj):
        if hasattr(obj.user, "profile"):
            return UserProfileSerializer(obj.user.profile).data
        return None

    def get_is_favorite(self, obj):
        favorite_ids = self.context.get("favorite_ids", [])
        return obj.id in favorite_ids

    # ✅ ONLY DISPLAY DISTANCE (NO CALCULATION HERE)
    def get_distance(self, obj):
        distance = getattr(obj, "distance", None)

        if distance is None:
            return None

        if distance < 1:
            return f"{round(distance * 1000)} m"
        return f"{round(distance, 2)} km"
    

    # service_amount = serializers.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    #     required=False,
    #     allow_null=True
    # )    