from django.db import models
from category.models import Category

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    subcategory_name = models.CharField(max_length=100)
    subcategory_image = models.ImageField(upload_to="subcategory/", null=True, blank=True)

    def __str__(self):
        return self.subcategory_name