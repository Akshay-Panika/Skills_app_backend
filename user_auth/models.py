from django.db import models

class UserAuth(models.Model):
    user_phone = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)  # OTP store ke liye
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_phone