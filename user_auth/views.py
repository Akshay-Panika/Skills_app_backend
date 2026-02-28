from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserAuth
from .serializers import UserAuthSerializer


class UserAuthCreateView(APIView):
    
    def post(self, request):
        phone = request.data.get("user_phone")
        verified = request.data.get("is_verified")

        # ❌ validation
        if not phone or verified is not True:
            return Response(
                {"error": "Phone and verified true required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔎 check existing user
        user = UserAuth.objects.filter(user_phone=phone).first()

        if user:
            serializer = UserAuthSerializer(user)
            return Response(
                {"message": "User already exists", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        # ✅ create new user
        user = UserAuth.objects.create(
            user_phone=phone,
            is_verified=True
        )

        serializer = UserAuthSerializer(user)

        return Response(
            {"message": "Account created", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    

class UserAuthListView(APIView):

    def get(self, request):
        users = UserAuth.objects.all().order_by("-id")
        serializer = UserAuthSerializer(users, many=True)

        return Response(
            {
                "count": users.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
