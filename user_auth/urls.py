from django.urls import path
from .views import SendOTPView, VerifyOTPView, UserAuthListView

urlpatterns = [
    path("auth/send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("auth/list/", UserAuthListView.as_view(), name="user_list"),
]