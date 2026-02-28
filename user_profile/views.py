from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_auth.models import UserAuth
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileCreateView(APIView):

    def post(self, request, pk):

        # 🔎 user check by id
        user = UserAuth.objects.filter(id=pk).first()
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 👉 existing profile check
        profile = getattr(user, "profile", None)

        # 👉 request data copy
        data = request.data.copy()

        # 🔥 phone always from DB (never update)
        data["user_phone"] = user.user_phone

        # 🟢 CREATE
        if not profile:
            serializer = UserProfileSerializer(data=data)

        # 🟡 UPDATE
        else:
            serializer = UserProfileSerializer(profile, data=data, partial=True)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
class UserProfileByIdView(APIView):

    def get(self, request, pk):
        profile = UserProfile.objects.filter(id=pk).first()

        if not profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)