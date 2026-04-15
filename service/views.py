from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .serializers import ServiceSerializer
from user_auth.models import UserAuth
from favorite.models import Favorite
from .utils.location import calculate_distance

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
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        favorite_ids = []
        distance_map = {}

        # ✅ favorites
        if user_id:
            try:
                user = UserAuth.objects.get(id=user_id)
                favorite_ids = list(
                    Favorite.objects.filter(user=user)
                    .values_list("service_id", flat=True)
                )
            except:
                pass

        # ✅ distance filtering
        if lat and lon:
            lat = float(lat)
            lon = float(lon)

            filtered_services = []

            for service in services:
                dist = calculate_distance(lat, lon, service.latitude, service.longitude)

                if dist is not None and dist <= 20:  # 🔥 20 KM filter
                    meters = dist * 1000

                    if meters < 1000:
                        distance_map[service.id] = f"{round(meters)} m"
                    else:
                        distance_map[service.id] = f"{round(dist, 2)} km"

                    filtered_services.append(service)

            services = filtered_services

        serializer = ServiceSerializer(
            services,
            many=True,
            context={
                "favorite_ids": favorite_ids,
                "distance_map": distance_map
            }
        )

        return Response({
            "count": len(services),
            "services": serializer.data
        })
    

class ServiceDetailView(APIView):
    def get(self, request, pk):
        try:
            service = Service.objects.select_related("user", "user__profile").get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=404)

        user_id = request.GET.get("user")
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        favorite_ids = []
        distance = None

        # ✅ favorite logic
        if user_id:
            favorite_ids = list(
                Favorite.objects.filter(user_id=user_id)
                .values_list("service_id", flat=True)
            )

        # ✅ distance logic
        if lat and lon:
            lat = float(lat)
            lon = float(lon)

            dist = calculate_distance(lat, lon, service.latitude, service.longitude)

            if dist is not None:
                meters = dist * 1000

                if meters < 1000:
                    distance = f"{round(meters)} m"   # 🔥 0 m bhi show hoga
                else:
                    distance = f"{round(dist, 2)} km"

        serializer = ServiceSerializer(
            service,
            context={
                "favorite_ids": favorite_ids,
                "distance": distance
            }
        )

        return Response(serializer.data)
    


# 4️⃣ List services by verified user
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

# 5️⃣ Update service
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