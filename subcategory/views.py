from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SubCategory
from .serializers import SubCategorySerializer
from category.models import Category


# 🔥 1. ALL SUBCATEGORIES (NO FILTER)
class AllSubCategoryView(APIView):

    def get(self, request):
        subcategories = SubCategory.objects.all()
        serializer = SubCategorySerializer(subcategories, many=True)

        return Response({
            "count": subcategories.count(),
            "data": serializer.data
        })


# 🔥 2. CATEGORY WISE + ADD
class SubCategoryByCategoryView(APIView):

    def get(self, request, category_id):
        category = Category.objects.filter(id=category_id).first()
        if not category:
            return Response({"error": "Category not found"}, status=404)

        subcategories = SubCategory.objects.filter(category=category)
        serializer = SubCategorySerializer(subcategories, many=True)

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

        serializer = SubCategorySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)


# 🔥 3. UPDATE + DELETE (single object)
class SubCategoryDetailView(APIView):

    def put(self, request, category_id, subcategory_id):
        subcategory = SubCategory.objects.filter(
            id=subcategory_id,
            category_id=category_id
        ).first()

        if not subcategory:
            return Response({"error": "SubCategory not found"}, status=404)

        serializer = SubCategorySerializer(
            subcategory,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


    def delete(self, request, category_id, subcategory_id):
        subcategory = SubCategory.objects.filter(
            id=subcategory_id,
            category_id=category_id
        ).first()

        if not subcategory:
            return Response({"error": "SubCategory not found"}, status=404)

        subcategory.delete()

        return Response({
            "message": "SubCategory deleted successfully",
            "success": True
        }, status=200)