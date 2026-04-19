from rest_framework import serializers
from .models import Service
from user_profile.serializers import UserProfileSerializer
from category.models import Category
from subcategory.models import SubCategory

class ServiceSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    service_image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    service_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    swipe_status = serializers.BooleanField(required=False)

    user_profile = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    
    category_id = serializers.PrimaryKeyRelatedField(
    queryset=Category.objects.all(),
    source='category',
    write_only=True
    )

    subcategory_id = serializers.PrimaryKeyRelatedField(
    queryset=SubCategory.objects.all(),
    source='subcategory',
    write_only=True
    )

    class Meta:
        model = Service
        exclude = ["user"]

    # 🔥 MAIN FIX HERE
    def get_distance(self, obj):
        # Detail view
        if "distance" in self.context:
            return self.context.get("distance")

        # List view
        return self.context.get("distance_map", {}).get(obj.id)

    def get_user_profile(self, obj):
        if hasattr(obj.user, "profile"):
            return UserProfileSerializer(obj.user.profile).data
        return None

    def get_is_favorite(self, obj):
        favorite_ids = self.context.get("favorite_ids", [])
        return obj.id in favorite_ids

    def validate(self, data):
        if data.get("service_status") and data.get("service_amount") is None:
            raise serializers.ValidationError({
                "service_amount": "This field is required when service_status is True."
            })
        return data

    def create(self, validated_data):
        if not validated_data.get("service_status"):
            validated_data["service_amount"] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not validated_data.get("service_status"):
            validated_data["service_amount"] = None
        return super().update(instance, validated_data)