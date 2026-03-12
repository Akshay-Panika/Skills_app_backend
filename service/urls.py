from django.urls import path
from .views import (
    ServiceCreateView,
    ServiceListView,
    ServiceDetailView
)

urlpatterns = [

    # Create Service
    path(
        "service/create/",
        ServiceCreateView.as_view(),
        name="create-service"
    ),

    # All Services List
    path(
        "service/list/",
        ServiceListView.as_view(),
        name="service-list"
    ),

    # Single Service Detail
    path(
        "service/detail/<int:pk>/",
        ServiceDetailView.as_view(),
        name="service-detail"
    ),

]