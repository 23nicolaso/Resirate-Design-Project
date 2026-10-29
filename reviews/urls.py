from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("buildings/<int:building_pk>/reviews/new/", views.review_create, name="review_create"),
    path("reviews/<int:pk>/edit/", views.review_edit, name="review_edit"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="review_delete"),
    path("buildings/<int:building_pk>/issues/new/", views.issue_create, name="issue_create"),
    path("issues/<int:pk>/edit/", views.issue_edit, name="issue_edit"),
    path("issues/<int:pk>/delete/", views.issue_delete, name="issue_delete"),
]
