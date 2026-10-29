from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("moderation/", include("moderation.urls")),
    path("", include("reviews.urls")),
    path("", include("buildings.urls")),
]
