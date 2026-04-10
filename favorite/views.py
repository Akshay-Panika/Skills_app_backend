from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Favorite
from user_auth.models import UserAuth
from service.models import Service
from service.serializers import ServiceSerializer  # 👈 needed


class ToggleFavoriteView(APIView):
    def post(self, request):
        user_id = request.data.get("user")
        service_id = request.data.get("service")

        try:
            user = UserAuth.objects.get(id=user_id)
            service = Service.objects.get(id=service_id)
        except:
            return Response(
                {"success": False, "message": "Invalid user or service"},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite, created = Favorite.objects.get_or_create(
            user=user,
            service=service
        )

        # ❌ Remove
        if not created:
            favorite.delete()
            return Response({
                "success": True,
                "message": "Removed from favorites"
            })

        # ❤️ Add
        return Response({
            "success": True,
            "message": "Added to favorites"
        })
    
class UserFavoriteListView(APIView):
    def get(self, request, user_id):
        try:
            user = UserAuth.objects.get(id=user_id)
        except UserAuth.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        favorites = Favorite.objects.filter(user=user).select_related("service")

        # 🔥 get all services
        services = [f.service for f in favorites]

        serializer = ServiceSerializer(services, many=True)

        return Response({
            "success": True,
            "count": len(serializer.data),
            "favorites": serializer.data
        })
    
class RemoveFavoriteView(APIView):
    def delete(self, request, user_id, service_id):
        try:
            fav = Favorite.objects.get(user_id=user_id, service_id=service_id)
            fav.delete()
            return Response({
                "success": True,
                "message": "Removed from favorites"
            })
        except Favorite.DoesNotExist:
            return Response({
                "success": False,
                "message": "Favorite not found"
            }, status=status.HTTP_404_NOT_FOUND)