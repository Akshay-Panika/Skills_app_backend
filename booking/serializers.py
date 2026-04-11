from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):

    service_name = serializers.CharField(source="service.service_name", read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"