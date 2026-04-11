from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user_auth.models import UserAuth
from service.models import Service
from .models import Booking
from .serializers import BookingSerializer


class CreateBookingView(APIView):
    def post(self, request):

        buyer_id = request.data.get("buyer")
        service_id = request.data.get("service")
        message = request.data.get("message", "")

        try:
            buyer = UserAuth.objects.get(id=buyer_id)
            service = Service.objects.get(id=service_id)
        except:
            return Response({"success": False, "error": "Invalid buyer or service"}, status=400)

        booking = Booking.objects.create(
            buyer=buyer,
            seller=service.user,
            service=service,
            message=message,
            status="pending"
        )

        return Response({
            "success": True,
            "message": "Booking created successfully",
            "data": BookingSerializer(booking).data
        }, status=201)
    

class UserBookingView(APIView):
    def get(self, request, user_id):

        buyer_bookings = Booking.objects.filter(buyer_id=user_id).order_by("-id")
        seller_bookings = Booking.objects.filter(seller_id=user_id).order_by("-id")

        return Response({
            "success": True,
            "data": {
                "buyer_bookings": BookingSerializer(buyer_bookings, many=True).data,
                "seller_bookings": BookingSerializer(seller_bookings, many=True).data
            },
            "counts": {
                "buyer_total": buyer_bookings.count(),
                "seller_total": seller_bookings.count(),
                "total": buyer_bookings.count() + seller_bookings.count()
            }
        })
    

class UpdateBookingStatusView(APIView):
    def patch(self, request, pk):

        status_value = request.data.get("status")

        valid_status = ["pending", "accepted", "rejected", "completed", "cancelled"]

        if status_value not in valid_status:
            return Response({"success": False, "error": "Invalid status"}, status=400)

        try:
            booking = Booking.objects.get(id=pk)
        except:
            return Response({"success": False, "error": "Booking not found"}, status=404)

        booking.status = status_value
        booking.save()

        return Response({
            "success": True,
            "message": "Status updated successfully",
            "data": BookingSerializer(booking).data
        })