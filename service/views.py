from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .serializers import ServiceSerializer
from user_auth.models import UserAuth
from favorite.models import Favorite
import math


def get_verified_user(user_id):
    try:
        user = UserAuth.objects.get(id=user_id)
        if not user.is_verified:
            return None, "User is not verified"
        return user, None
    except UserAuth.DoesNotExist:
        return None, "User not found"

class ServiceCreateView(APIView):
    def post(self, request):
        user_id = request.data.get("user")

        if not user_id:
            return Response({"error": "User id is required"}, status=400)

        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=400)

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

class ServiceListView(APIView):
    def get(self, request):

        user_lat = request.GET.get("latitude")
        user_lng = request.GET.get("longitude")
        user_id = request.GET.get("user")

        services = Service.objects.select_related("user", "user__profile").all()

        filtered_services = []
        favorite_ids = []

        # ✅ Favorite
        if user_id:
            favorite_ids = list(
                Favorite.objects.filter(user_id=user_id)
                .values_list("service_id", flat=True)
            )

        # ✅ Location filter
        if user_lat and user_lng:
            try:
                user_lat = float(user_lat)
                user_lng = float(user_lng)
            except:
                return Response({"error": "Invalid latitude/longitude"}, status=400)

            for service in services:
                if service.latitude and service.longitude:

                    # 🌍 Distance Calculation
                    R = 6371
                    lat1 = math.radians(user_lat)
                    lon1 = math.radians(user_lng)
                    lat2 = math.radians(service.latitude)
                    lon2 = math.radians(service.longitude)

                    dlat = lat2 - lat1
                    dlon = lon2 - lon1

                    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

                    distance = R * c

                    service.distance = distance

                    if distance <= 20:
                        filtered_services.append(service)

        else:
            filtered_services = list(services)

        # ✅ Sort nearest
        filtered_services.sort(key=lambda x: getattr(x, "distance", 9999))

        serializer = ServiceSerializer(
            filtered_services,
            many=True,
            context={"favorite_ids": favorite_ids}
        )

        return Response({
            "count": len(filtered_services),
            "services": serializer.data
        })

class ServiceDetailView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.select_related("user", "user__profile").get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)

        serializer = ServiceSerializer(service)
        return Response(serializer.data)

class ServiceListByUserView(APIView):
    def get(self, request, user_id):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        services = Service.objects.select_related("user", "user__profile").filter(user=user).order_by("-id")
        # services = Service.objects.filter(user=user).order_by("-id")
        serializer = ServiceSerializer(services, many=True)
        return Response({
            "count": services.count(),
            "services": serializer.data
        })

class ServiceUpdateView(APIView):
    def put(self, request, user_id, pk):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.select_related("user", "user__profile").get(id=pk, user=user)
            # service = Service.objects.get(id=pk, user=user)
        except Service.DoesNotExist:
            return Response({"error": "Service not found or you don't own it"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=user)  # ensure ownership
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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