from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .serializers import ServiceSerializer
from user_auth.models import UserAuth
from favorite.models import Favorite
from utils.location import calculate_distance

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

class ServiceListView(APIView):
    def get(self, request):

        user_lat = request.GET.get("lat")
        user_lng = request.GET.get("lng")

        services = Service.objects.select_related("user", "user__profile").all()

        user_id = request.GET.get("user")
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

        filtered_services = []

        for service in services:
            distance = None

            if (
                user_lat and user_lng and
                service.latitude is not None and
                service.longitude is not None
            ):
                distance = calculate_distance(
                    float(user_lat),
                    float(user_lng),
                    service.latitude,
                    service.longitude
                )

            if distance is None or distance <= 20:
                service.distance_km = distance
                filtered_services.append(service)

        serializer = ServiceSerializer(
            filtered_services,
            many=True,
            context={
                "favorite_ids": favorite_ids,
                "user_lat": user_lat,
                "user_lng": user_lng
            }
        )

        return Response({
            "count": len(filtered_services),
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