from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "classifier"

urlpatterns = [
    path("", views.classify_document, name="overview"),
    path("upload/", views.upload_files, name="upload_files"),
    path("results/", views.ResultHistory.as_view(), name="get_history")
]
