from django.urls import path
from .views import SubCategoryByCategoryView, SubCategoryDeleteView

urlpatterns = [
    path("subcategory/<int:category_id>/", SubCategoryByCategoryView.as_view()),
    path("subcategory/<int:category_id>/<int:subcategory_id>/", SubCategoryDeleteView.as_view()),
]