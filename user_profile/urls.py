from django.urls import path
from .views import ProfileAPIView

urlpatterns = [
    path('profiles/', ProfileAPIView.as_view()),
    path('profiles/<int:user_id>/', ProfileAPIView.as_view()),
]