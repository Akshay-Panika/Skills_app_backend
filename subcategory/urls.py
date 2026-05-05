from django.urls import path
from .views import (
    AllSubCategoryView,
    SubCategoryByCategoryView,
    SubCategoryDetailView
)

urlpatterns = [
    # 🔥 ALL SUBCATEGORIES
    path("subcategory/", AllSubCategoryView.as_view()),

    # 🔥 CATEGORY WISE + ADD
    path("subcategory/<int:category_id>/", SubCategoryByCategoryView.as_view()),

    # 🔥 UPDATE + DELETE
    path("subcategory/<int:category_id>/<int:subcategory_id>/", SubCategoryDetailView.as_view()),
]