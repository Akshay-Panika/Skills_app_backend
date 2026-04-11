from rest_framework import serializers
from .models import Booking
from service.serializers import ServiceSerializer


class BookingSerializer(serializers.ModelSerializer):

    service = ServiceSerializer(read_only=True)  

    class Meta:
        model = Booking
        fields = "__all__"