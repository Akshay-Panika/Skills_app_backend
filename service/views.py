from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .serializers import ServiceSerializer
from user_auth.models import UserAuth
from favorite.models import Favorite
import math


# ✅ DISTANCE CALCULATION
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ✅ COMMON FORMAT FUNCTION (USE EVERYWHERE)
def get_distance_text(distance_km):
    if distance_km is None:
        return None

    if distance_km < 0.05:
        return "Near you"
    elif distance_km < 1:
        return f"{int(distance_km * 1000)} m"
    else:
        return f"{round(distance_km, 2)} km"


def calculate_distance(user_lat, user_lon, service):
    if service.latitude is None or service.longitude is None:
        return None

    return haversine_distance(
        user_lat,
        user_lon,
        service.latitude,
        service.longitude
    )


def get_verified_user(user_id):
    try:
        user = UserAuth.objects.get(id=user_id)
        if not user.is_verified:
            return None, "User is not verified"
        return user, None
    except UserAuth.DoesNotExist:
        return None, "User not found"


# ✅ CREATE
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


# ✅ LIST (FIXED)
class ServiceListView(APIView):
    def get(self, request):
        services = Service.objects.select_related(
            "user", "user__profile"
        ).all().order_by("-id")

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

        # ✅ location parse
        use_location = False
        user_lat = user_lon = None

        if latitude and longitude:
            try:
                user_lat = float(latitude)
                user_lon = float(longitude)
                use_location = True
            except ValueError:
                pass

        result = []

        for service in services:
            distance_km = None

            if use_location:
                distance_km = calculate_distance(user_lat, user_lon, service)

                # 20 km filter
                if distance_km is None or distance_km > 20:
                    continue

            serializer = ServiceSerializer(
                service,
                context={"favorite_ids": favorite_ids}
            )

            data = serializer.data
            data["distance"] = get_distance_text(distance_km)

            result.append((data, distance_km))

        # ✅ SORT BY DISTANCE
        if use_location:
            result.sort(key=lambda x: x[1] if x[1] is not None else 9999)

        return Response({
            "count": len(result),
            "services": [item[0] for item in result]
        })


# ✅ DETAIL (SAME LOGIC)
class ServiceDetailView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.select_related(
                "user", "user__profile"
            ).get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)

        user_id = request.GET.get("user")
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")

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

        data = serializer.data

        # ✅ distance
        distance_km = None

        if latitude and longitude:
            try:
                user_lat = float(latitude)
                user_lon = float(longitude)

                distance_km = calculate_distance(user_lat, user_lon, service)
            except ValueError:
                pass

        data["distance"] = get_distance_text(distance_km)

        return Response(data)


# ✅ USER SERVICES
class ServiceListByUserView(APIView):
    def get(self, request, user_id):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=400)

        services = Service.objects.select_related(
            "user", "user__profile"
        ).filter(user=user).order_by("-id")

        serializer = ServiceSerializer(services, many=True)

        return Response({
            "count": services.count(),
            "services": serializer.data
        })


# ✅ UPDATE
class ServiceUpdateView(APIView):
    def put(self, request, user_id, pk):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=400)

        try:
            service = Service.objects.get(id=pk, user=user)
        except Service.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = ServiceSerializer(service, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


# ✅ DELETE
class ServiceDeleteView(APIView):
    def delete(self, request, user_id, pk):
        user, error = get_verified_user(user_id)
        if error:
            return Response({"error": error}, status=400)

        try:
            service = Service.objects.get(id=pk, user=user)
            service.delete()
            return Response({"message": "Deleted"}, status=200)
        except Service.DoesNotExist:
            return Response({"error": "Not found"}, status=404)