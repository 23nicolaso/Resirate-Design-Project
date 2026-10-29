from django.urls import path

from . import views

app_name = "buildings"

urlpatterns = [
    path("", views.search, name="search"),
    path("buildings/<int:pk>/", views.detail, name="detail"),
]