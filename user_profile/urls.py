from django.urls import path
from .views import UserProfileCreateView, UserProfileByIdView

urlpatterns = [
    path("profile/create/<int:pk>/", UserProfileCreateView.as_view()),
    path("profile/<int:pk>/", UserProfileByIdView.as_view()),
]