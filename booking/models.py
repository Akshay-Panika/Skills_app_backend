from django.db import models
from user_auth.models import UserAuth
from service.models import Service

class Booking(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="bookings")

    buyer = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="buyer_bookings"
    )

    seller = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="seller_bookings"
    )

    message = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.buyer.user_phone} -> {self.service.service_name}"