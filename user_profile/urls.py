from django.urls import path
from .views import ProfileAPIView

urlpatterns = [
    path("profiles/", ProfileAPIView.as_view()),        # GET all
    path("profile/update/<int:id>/", ProfileAPIView.as_view())  # PUT by id
]