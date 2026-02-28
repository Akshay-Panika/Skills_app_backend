from django.urls import path
from .views import UserAuthCreateView, UserAuthListView 

urlpatterns = [
    path("auth/", UserAuthCreateView.as_view()),
    path("auth/list/", UserAuthListView.as_view()),

]