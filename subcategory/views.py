from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SubCategory
from .serializers import SubCategorySerializer
from category.models import Category


class SubCategoryByCategoryView(APIView):

    # ✅ GET (list)
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


    # ✅ POST (add)
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

# ✅ DELETE Separate View (clean URL)
class SubCategoryDeleteView(APIView):

    def delete(self, request, category_id, subcategory_id):
        subcategory = SubCategory.objects.filter(
            id=subcategory_id,
            category_id=category_id
        ).first()

        if not subcategory:
            return Response({"error": "SubCategory not found"}, status=404)

        subcategory.delete()
        return Response({"message": "Deleted successfully"}, status=204)