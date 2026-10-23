from django.urls import path
from .views import (
    ToggleFavoriteView,
    UserFavoriteListView,
    RemoveFavoriteView
)

urlpatterns = [
    path("favorite/toggle/", ToggleFavoriteView.as_view()),
    path("favorite/user/<int:user_id>/", UserFavoriteListView.as_view()),
    path("favorite/remove/<int:user_id>/<int:service_id>/", RemoveFavoriteView.as_view()),
]