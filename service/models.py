from django.db import models
from cloudinary.models import CloudinaryField
from user_auth.models import UserAuth
from category.models import Category
from subcategory.models import SubCategory

class Service(models.Model):
    user = models.ForeignKey(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="services"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE
    )
    service_name = models.CharField(max_length=255)

    #  CloudinaryField for image
    service_image = CloudinaryField(
        'image',
        folder='services',
        blank=True,
        null=True
    )

    service_status = models.BooleanField(default=True)
    swipe_status = models.BooleanField(default=False)  # 🔹 New field

    # service_amount required only if service_status=True
    service_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    service_description = models.TextField(
        null=True,
        blank=True
    )

    # 🔹 Latitude & Longitude for location-based search
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    is_booked = models.BooleanField(default=False)
    # 🔹 Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Creation time
    updated_at = models.DateTimeField(auto_now=True)      # Last updated time

    def __str__(self):
        return self.service_name