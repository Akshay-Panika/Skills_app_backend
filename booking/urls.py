from django.urls import path
from .views import (
    CreateBookingView,
    UserBookingView,
    UpdateBookingStatusView,
    DeleteBookingView,
    CheckBookingView
)

urlpatterns = [
    path("booking/create/", CreateBookingView.as_view()),
    path("booking/user/<int:user_id>/", UserBookingView.as_view()),
    path("booking/update/<int:pk>/", UpdateBookingStatusView.as_view()),
    path("booking/delete/<int:pk>/<int:user_id>/", DeleteBookingView.as_view()),
    path("booking/check/", CheckBookingView.as_view()),
    
]