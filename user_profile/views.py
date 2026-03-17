from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import UserProfile
from .serializers import UserProfileSerializer


class ProfileAPIView(APIView):

    # ✅ Required for image upload
    parser_classes = (MultiPartParser, FormParser)

    # GET
    def get(self, request, user_id=None):

        if user_id:
            profile = UserProfile.objects.filter(user=user_id).first()

            if not profile:
                return Response({"error": "Profile not found"}, status=404)

            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)

        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)

        return Response({
            "count": profiles.count(),
            "profiles": serializer.data
        })


    # PUT (Update profile)
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