from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("user_auth.urls")),
    path("api/", include("user_profile.urls")),
    path("api/", include("category.urls")),
    path("api/", include("subcategory.urls")),
    path("api/", include("service.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
