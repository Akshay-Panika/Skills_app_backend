from django.urls import path
from .views import (
    ServiceCreateView,
    ServiceListView,
    ServiceDetailView
)

urlpatterns = [
    path("service/create/", ServiceCreateView.as_view(), name="create-service"),
    path("service/list/", ServiceListView.as_view(), name="service-list"),
    path("service/detail/<int:pk>/", ServiceDetailView.as_view(), name="service-detail"),
]