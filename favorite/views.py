from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Favorite
from user_auth.models import UserAuth
from service.models import Service


class ToggleFavoriteView(APIView):
    def post(self, request):
        user_id = request.data.get("user")
        service_id = request.data.get("service")

        try:
            user = UserAuth.objects.get(id=user_id)
            service = Service.objects.get(id=service_id)
        except:
            return Response({"error": "Invalid user or service"}, status=400)

        favorite, created = Favorite.objects.get_or_create(
            user=user,
            service=service
        )

        if not created:
            favorite.delete()
            return Response({"message": "Removed from favorites ❌"})

        return Response({"message": "Added to favorites ❤️"})
    

class UserFavoriteListView(APIView):
    def get(self, request, user_id):
        try:
            user = UserAuth.objects.get(id=user_id)
        except UserAuth.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        favorites = Favorite.objects.filter(user=user).select_related("service")

        data = [
            {
                "favorite_id": f.id,
                "service_id": f.service.id,
                "service_name": f.service.service_name,
                "service_image": f.service.service_image.url if f.service.service_image else None,
            }
            for f in favorites
        ]

        return Response({
            "count": favorites.count(),
            "favorites": data
        })
        

class RemoveFavoriteView(APIView):
    def delete(self, request, user_id, service_id):
        try:
            fav = Favorite.objects.get(user_id=user_id, service_id=service_id)
            fav.delete()
            return Response({"message": "Removed successfully"})
        except Favorite.DoesNotExist:
            return Response({"error": "Not found"}, status=404)        