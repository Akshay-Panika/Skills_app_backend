from rest_framework import serializers
from .models import Service
from user_profile.serializers import UserProfileSerializer
import math


class ServiceSerializer(serializers.ModelSerializer):
    service_image = serializers.ImageField(use_url=True, required=False, allow_null=True)

    service_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    swipe_status = serializers.BooleanField(required=False)

    user_profile = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    # 🔥 NEW FIELD
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Service
        exclude = ["user"]

    # 🔹 USER PROFILE
    def get_user_profile(self, obj):
        if hasattr(obj.user, "profile"):
            return UserProfileSerializer(obj.user.profile).data
        return None

    # 🔹 FAVORITE CHECK
    def get_is_favorite(self, obj):
        favorite_ids = self.context.get("favorite_ids", [])
        return obj.id in favorite_ids

    # 🔥 DISTANCE CALCULATION
    def get_distance(self, obj):
        user_lat = self.context.get("user_lat")
        user_lng = self.context.get("user_lng")

        # ❌ Safety check
        if not user_lat or not user_lng:
            return None

        if not obj.latitude or not obj.longitude:
            return None

        try:
            user_lat = float(user_lat)
            user_lng = float(user_lng)
        except:
            return None

        # 🌍 Haversine Formula
        R = 6371  # Earth radius in KM

        lat1 = math.radians(user_lat)
        lon1 = math.radians(user_lng)
        lat2 = math.radians(obj.latitude)
        lon2 = math.radians(obj.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c  # KM

        # 🎯 Format response
        if distance < 1:
            return f"{round(distance * 1000)} m"
        return f"{round(distance, 2)} km"

    # 🔹 VALIDATION
    def validate(self, data):
        if data.get("service_status") and data.get("service_amount") is None:
            raise serializers.ValidationError({
                "service_amount": "This field is required when service_status is True."
            })
        return data

    # 🔹 CREATE
    def create(self, validated_data):
        if not validated_data.get("service_status"):
            validated_data["service_amount"] = None
        return super().create(validated_data)

    # 🔹 UPDATE
    def update(self, instance, validated_data):
        if not validated_data.get("service_status"):
            validated_data["service_amount"] = None
        return super().update(instance, validated_data)