from rest_framework import serializers
from .models import SubCategory

class SubCategorySerializer(serializers.ModelSerializer):
    subcategory_image = serializers.ImageField(required=False)

    class Meta:
        model = SubCategory
        fields = ["id", "category", "subcategory_name", "subcategory_image"]

    def validate(self, data):
        category = data.get("category") or getattr(self.instance, "category", None)
        name = data.get("subcategory_name") or getattr(self.instance, "subcategory_name", None)

        qs = SubCategory.objects.filter(category=category, subcategory_name__iexact=name)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError({
                "subcategory_name": "This subcategory already exists in this category."
            })

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Cloudinary ka URL directly
        representation["subcategory_image"] = str(instance.subcategory_image.url) if instance.subcategory_image else None
        representation["category_name"] = instance.category.category_name
        return representation