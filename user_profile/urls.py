from django.urls import path
from .views import UserProfileCreateByPhoneView, UserProfileByPhoneView

urlpatterns = [
    path("profile/create/<str:phone>/", UserProfileCreateByPhoneView.as_view()),
    path("profile/by-phone/<str:phone>/", UserProfileByPhoneView.as_view()),
]