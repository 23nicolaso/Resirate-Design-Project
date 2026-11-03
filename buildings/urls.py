from django.urls import path

from . import views

app_name = "buildings"

urlpatterns = [
    path("api/addresses/suggestions/", views.address_suggestions, name="address_suggestions"),
    path("buildings/resolve/", views.resolve_address, name="resolve_address"),
    path("", views.search, name="search"),
    path("buildings/<int:pk>/", views.detail, name="detail"),
]