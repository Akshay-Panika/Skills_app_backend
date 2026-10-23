from django.db import models
from category.models import Category
from cloudinary.models import CloudinaryField

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    subcategory_name = models.CharField(max_length=100)
    subcategory_image = CloudinaryField('image', folder='subcategory', blank=True, null=True)

    def __str__(self):
        return self.subcategory_name