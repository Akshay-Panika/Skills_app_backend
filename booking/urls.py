from django.urls import path
from .views import (
    CreateBookingView,
    UserBookingView,
    UpdateBookingStatusView
)

urlpatterns = [
    path("booking/create/", CreateBookingView.as_view()),
    path("booking/user/<int:user_id>/", UserBookingView.as_view()),
    path("booking/update/<int:pk>/", UpdateBookingStatusView.as_view()),
]