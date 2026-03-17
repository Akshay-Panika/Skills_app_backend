from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):

    user_image = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user", "user_phone"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user_image"] = (
            instance.user_image.url
            if instance.user_image else None
        )

        return data   # ✅ comma हटाया