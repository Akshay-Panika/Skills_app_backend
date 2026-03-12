from django.urls import path
from .views import SubCategoryByCategoryView

urlpatterns = [
    path("subcategory/<int:category_id>/", SubCategoryByCategoryView.as_view()),
]