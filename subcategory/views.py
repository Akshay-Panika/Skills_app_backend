from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SubCategory
from .serializers import SubCategorySerializer
from category.models import Category

class SubCategoryByCategoryView(APIView):
    def get(self, request, category_id):
        category = Category.objects.filter(id=category_id).first()
        if not category:
            return Response({"error": "Category not found"}, status=404)

        subcategories = SubCategory.objects.filter(category=category)
        serializer = SubCategorySerializer(subcategories, many=True, context={"request": request})

        return Response({
            "category": category.category_name,
            "count": subcategories.count(),
            "data": serializer.data
        })

    def post(self, request, category_id):
        category = Category.objects.filter(id=category_id).first()
        if not category:
            return Response({"error": "Category not found"}, status=404)

        data = request.data.copy()
        data["category"] = category.id

        serializer = SubCategorySerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)