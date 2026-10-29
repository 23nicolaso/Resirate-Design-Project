from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("reviews/", views.my_reviews, name="my_reviews"),
    path("issues/", views.my_issues, name="my_issues"),
]
