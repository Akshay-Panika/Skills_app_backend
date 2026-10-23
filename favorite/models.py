from django.db import models
from user_auth.models import UserAuth
from service.models import Service

class Favorite(models.Model):
    user = models.ForeignKey(UserAuth, on_delete=models.CASCADE, related_name="favorites")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="favorited_by")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'service')  # 🔥 duplicate favorite prevent

    def __str__(self):
        return f"{self.user.user_phone} -> {self.service.service_name}"