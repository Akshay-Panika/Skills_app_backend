from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserAuth
from .serializers import UserAuthSerializer, OTPVerifySerializer
from .twilio_client import send_otp

# 1️⃣ Send OTP to user
class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get("user_phone")
        if not phone:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = send_otp(phone)
        user, created = UserAuth.objects.get_or_create(user_phone=phone)
        user.otp = otp
        user.save()
        
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

# 2️⃣ Verify OTP
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['user_phone']
            otp = serializer.validated_data['otp']

            try:
                user = UserAuth.objects.get(user_phone=phone)
            except UserAuth.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user.otp == otp:
                user.is_verified = True
                user.otp = ""  # clear OTP after verification
                user.save()
                user_serializer = UserAuthSerializer(user)
                return Response({"message": "Phone verified", "data": user_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3️⃣ List users (existing)
class UserAuthListView(APIView):
    def get(self, request):
        users = UserAuth.objects.all().order_by("-id")
        serializer = UserAuthSerializer(users, many=True)
        return Response({"count": users.count(), "data": serializer.data}, status=status.HTTP_200_OK)