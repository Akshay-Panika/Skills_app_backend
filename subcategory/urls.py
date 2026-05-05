from django.urls import path
from .views import SubCategoryByCategoryView

urlpatterns = [
    # GET + POST
    path("subcategory/<int:category_id>/", SubCategoryByCategoryView.as_view()),

    path("subcategory/<int:category_id>/<int:subcategory_id>/", SubCategoryByCategoryView.as_view()),
]