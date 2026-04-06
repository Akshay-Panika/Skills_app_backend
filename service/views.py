from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .serializers import ServiceSerializer
from user_auth.models import UserAuth

# 🔹 Helper to get verified user
def get_verified_user(user_id):
    try:
        user = UserAuth.objects.get(id=user_id)
        if not user.is_verified:
            return None, "User is not verified"
        return user, None
    except UserAuth.DoesNotExist:
        return None, "User not found"

# 1️⃣ Create Service
class ServiceCreateView(APIView):
    def post(self, request):
        user_id = request.data.get("user")
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2️⃣ List all services
class ServiceListView(APIView):
    def get(self, request):
        services = Service.objects.all().order_by("-id")
        serializer = ServiceSerializer(services, many=True)
        return Response({
            "count": services.count(),
            "services": serializer.data
        })

# 3️⃣ Get service details by ID
class ServiceDetailView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

# 4️⃣ List services by verified user
class ServiceListByUserView(APIView):
    def get(self, request, user_id):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        services = Service.objects.filter(user=user).order_by("-id")
        serializer = ServiceSerializer(services, many=True)
        return Response({
            "count": services.count(),
            "services": serializer.data
        })

# 5️⃣ Update service
class ServiceUpdateView(APIView):
    def put(self, request, user_id, pk):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.get(id=pk, user=user)
        except Service.DoesNotExist:
            return Response({"error": "Service not found or you don't own it"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=user)  # ensure ownership
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 6️⃣ Delete service
class ServiceDeleteView(APIView):
    def delete(self, request, user_id, pk):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.get(id=pk, user=user)
            service.delete()
            return Response({"message": "Service deleted successfully"}, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response({"error": "Service not found or you don't own it"}, status=status.HTTP_404_NOT_FOUND)