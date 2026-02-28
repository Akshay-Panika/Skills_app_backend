from django.db import models
from user_auth.models import UserAuth


class UserProfile(models.Model):
    user = models.OneToOneField(
        UserAuth,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    user_name = models.CharField(max_length=100)
    user_phone = models.CharField(max_length=15)
    user_email = models.EmailField(blank=True, null=True)
    user_gender = models.CharField(max_length=10)
    user_bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user_name