from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .serializers import ServiceSerializer
from user_auth.models import UserAuth
from favorite.models import Favorite
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Returns distance in kilometers between two lat/lon points."""
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

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
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ServiceListView(APIView):
    def get(self, request):
        services = Service.objects.select_related("user", "user__profile").all().order_by("-id")

        user_id = request.GET.get("user")
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")

        favorite_ids = []

        if user_id:
            try:
                user = UserAuth.objects.get(id=user_id)
                favorite_ids = list(
                    Favorite.objects.filter(user=user)
                    .values_list("service_id", flat=True)
                )
            except UserAuth.DoesNotExist:
                pass

        # ✅ Location-based filtering (20km radius)
        filtered_services = []
        use_location_filter = False

        if latitude and longitude and latitude.strip() and longitude.strip():
            try:
                user_lat = float(latitude.strip())
                user_lon = float(longitude.strip())
                use_location_filter = True
            except ValueError:
                use_location_filter = False

        for service in services:
            if use_location_filter:
                if service.latitude is None or service.longitude is None:
                    continue  # skip services without location
                distance_km = haversine_distance(user_lat, user_lon, service.latitude, service.longitude)
                if distance_km <= 20:
                    filtered_services.append((service, round(distance_km, 2)))
            else:
                filtered_services.append((service, None))

        # Sort by distance (nearest first) if filtering
        if use_location_filter:
            filtered_services.sort(key=lambda x: x[1])

        # Serialize
        result = []
        for service, distance in filtered_services:
            serializer = ServiceSerializer(
                service,
                context={"favorite_ids": favorite_ids}
            )
            data = serializer.data
            if distance is not None:
                # ✅ Human-readable distance
                if distance < 1:
                    data["distance"] = f"{int(distance * 1000)} m"
                else:
                    data["distance"] = f"{distance} km"
            else:
                data["distance"] = None
            result.append(data)

        return Response({
            "count": len(result),
            "services": result
        })
    
class ServiceDetailView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.select_related("user", "user__profile").get(id=pk)
            # service = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)

        user_id = request.GET.get("user")
        favorite_ids = []

        if user_id:
            favorite_ids = list(
                Favorite.objects.filter(user_id=user_id)
                .values_list("service_id", flat=True)
            )

        serializer = ServiceSerializer(
            service,
            context={"favorite_ids": favorite_ids}
        )

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