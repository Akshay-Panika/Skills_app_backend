from django.urls import path
from .views import (
    ServiceCreateView,
    ServiceListView,
    ServiceDetailView,
    ServiceListByUserView,
    ServiceUpdateView,
    ServiceDeleteView,
    ServiceSearchView
)

urlpatterns = [
    path("service/search/",ServiceSearchView.as_view(),name="search-service"),
    path("service/create/", ServiceCreateView.as_view(), name="create-service"),
    path("service/list/", ServiceListView.as_view(), name="all-services"),
    path("service/<int:pk>/", ServiceDetailView.as_view(), name="service-detail"),

    path("service/user/<int:user_id>/", ServiceListByUserView.as_view(), name="user-services"),
    path("service/user/<int:user_id>/update/<int:pk>/", ServiceUpdateView.as_view(), name="update-service"),

    path("service/user/<int:user_id>/bulk-delete/", ServiceDeleteView.as_view(), name="delete-service"),

]

# /api/service/list/
# /api/service/list/?lat=18.51&lon=73.93
# /api/service/97/?lat=18.51&lon=73.93
# /api/service/user/1/
# /api/service/user/1/update/97/