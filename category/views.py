from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer


class CategoryCRUDView(APIView):

    # 🔹 GET (list + single)
    def get(self, request, pk=None):
        if pk:
            category = Category.objects.filter(id=pk).first()
            if not category:
                return Response({"error": "Category not found"}, status=404)

            serializer = CategorySerializer(category)
            return Response(serializer.data)

        categories = Category.objects.all().order_by("-id")
        serializer = CategorySerializer(categories, many=True)

        return Response({
            "count": categories.count(),
            "data": serializer.data
        })

    # 🔹 POST (create)
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    # 🔹 PUT / PATCH (update)
    def put(self, request, pk):
        category = Category.objects.filter(id=pk).first()
        if not category:
            return Response({"error": "Category not found"}, status=404)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    # 🔹 DELETE
    def delete(self, request, pk):
        category = Category.objects.filter(id=pk).first()
        if not category:
            return Response({"error": "Category not found"}, status=404)

        category.delete()
        return Response({"message": "Category deleted successfully"}, status=200)