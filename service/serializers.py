from rest_framework import serializers
from .models import Service
from user_profile.serializers import UserProfileSerializer


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


    class Meta:
        model = Service
        exclude = ["user"]
        # fields = "__all__"


    def get_user_profile(self, obj):
        if hasattr(obj.user, "profile"):
            return UserProfileSerializer(obj.user.profile).data
        return None    

    def get_is_favorite(self, obj):
        favorite_ids = self.context.get("favorite_ids", [])
        return obj.id in favorite_ids    

    def validate(self, data):
        # ✅ service_amount required only if service_status=True
        if data.get("service_status") and data.get("service_amount") is None:
            raise serializers.ValidationError({
                "service_amount": "This field is required when service_status is True."
            })
        return data

    def create(self, validated_data):
        # 🔹 Set service_amount=None if service_status=False
        if not validated_data.get("service_status"):
            validated_data["service_amount"] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 🔹 Set service_amount=None if service_status=False
        if not validated_data.get("service_status"):
            validated_data["service_amount"] = None
        return super().update(instance, validated_data)