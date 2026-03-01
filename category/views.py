from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer

class CategoryCRUDView(APIView):
    # 🔹 GET list or single
    def get(self, request, pk=None):
        if pk:
            category = Category.objects.filter(id=pk).first()
            if not category:
                return Response({"error": "Category not found"}, status=404)
            serializer = CategorySerializer(category, context={"request": request})
            return Response(serializer.data)

        categories = Category.objects.all().order_by("-id")
        serializer = CategorySerializer(categories, many=True, context={"request": request})
        return Response({
            "count": categories.count(),
            "data": serializer.data
        })

    # 🔹 POST (image upload)
    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)  # Exact error if invalid
        serializer.save()
        return Response(serializer.data, status=201)

    # 🔹 PUT / PATCH
    def put(self, request, pk):
        category = Category.objects.filter(id=pk).first()
        if not category:
            return Response({"error": "Category not found"}, status=404)

        serializer = CategorySerializer(category, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # 🔹 DELETE
    def delete(self, request, pk):
        category = Category.objects.filter(id=pk).first()
        if not category:
            return Response({"error": "Category not found"}, status=404)
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=200)