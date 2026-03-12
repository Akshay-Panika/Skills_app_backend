from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileSerializer


class ProfileAPIView(APIView):

    # ✅ Get all profiles
    def get(self, request):
        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)

        return Response({
            "count": profiles.count(),
            "profiles": serializer.data
        })

    # ✅ Update profile by USER ID
    def put(self, request, user_id):

        profile = UserProfile.objects.filter(user=user_id).first()

        if not profile:
            return Response({"error": "Profile not found"}, status=404)

        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)