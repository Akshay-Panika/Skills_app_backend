from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    category_image = serializers.ImageField(required=False)

    class Meta:
        model = Category
        fields = ["id", "category_name", "category_image"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["category_image"] = str(instance.category_image.url) if instance.category_image else None
        return representation   
