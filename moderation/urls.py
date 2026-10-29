from django.urls import path

from . import views

app_name = "moderation"

urlpatterns = [
    path("reviews/<int:pk>/report/", views.report_review, name="report_review"),
    path("issues/<int:pk>/report/", views.report_issue, name="report_issue"),
    path("", views.queue, name="queue"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/resolve/", views.resolve_report, name="resolve_report"),
]
