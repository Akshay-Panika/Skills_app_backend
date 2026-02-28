from django.urls import path
from .views import CategoryCRUDView

urlpatterns = [
    path("category/", CategoryCRUDView.as_view()),          # GET list, POST
    path("category/<int:pk>/", CategoryCRUDView.as_view()), # GET single, PUT, DELETE
]