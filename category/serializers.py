from rest_framework import serializers
from django.conf import settings
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    category_image = serializers.ImageField(required=False)

    class Meta:
        model = Category
        fields = ["id", "category_name", "category_image"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        if instance.category_image:
            url = instance.category_image.url
            # If in local development and the URL is relative, make it absolute
            if settings.DEBUG and not url.startswith("http"):
                url = request.build_absolute_uri(url)
            representation["category_image"] = url
        else:
            representation["category_image"] = None

        return representation  

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     request = self.context.get("request")

    #     if instance.category_image and request:
    #         representation["category_image"] = request.build_absolute_uri(instance.category_image.url)
    #     else:
    #         representation["category_image"] = None

    #     return representation