from django.urls import path
from .views import CategoryCRUDView

urlpatterns = [
    path("category/", CategoryCRUDView.as_view()),         
    path("category/<int:pk>/", CategoryCRUDView.as_view()),
]