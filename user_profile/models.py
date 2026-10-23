from django.db import models
from user_auth.models import UserAuth
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):

    user = models.OneToOneField(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    user_phone = models.CharField(max_length=15)
    user_name = models.CharField(max_length=100, blank=True, null=True)
    user_email = models.EmailField(blank=True, null=True)
    user_gender = models.CharField(max_length=10, blank=True, null=True)
    user_bio = models.TextField(blank=True, null=True)

    user_image = CloudinaryField(
        'image',
        folder='user_profile',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user_phone