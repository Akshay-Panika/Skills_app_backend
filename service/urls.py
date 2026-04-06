from django.urls import path
from .views import (
    ServiceCreateView,
    ServiceListView,
    ServiceDetailView,
    ServiceListByUserView,
    ServiceUpdateView,
    ServiceDeleteView
)

urlpatterns = [
    # ✅ Create
    path("service/create/", ServiceCreateView.as_view(), name="create-service"),

    # ✅ All services
    path("service/list/", ServiceListView.as_view(), name="all-services"),

    # ✅ Single service detail
    path("service/<int:pk>/", ServiceDetailView.as_view(), name="service-detail"),

    # ✅ Services by user
    path("service/user/<int:user_id>/", ServiceListByUserView.as_view(), name="user-services"),

    # ✅ Update (FIXED)
    path("service/user/<int:user_id>/update/<int:pk>/", ServiceUpdateView.as_view(), name="update-service"),

    # ✅ Delete (FIXED)
    path("service/user/<int:user_id>/delete/<int:pk>/", ServiceDeleteView.as_view(), name="delete-service"),
]