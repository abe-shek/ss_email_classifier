from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "user"

urlpatterns = [
    path("", RedirectView.as_view(url="/login"), name="index"),
    path("login/", views.login_user, name="login_user"),
    path("logout/", views.logout_user, name="logout_user"),
    path("register/", views.register_user, name="register_user"),
    path("change_password/", views.change_password, name="change_password"),
    path("profile/", views.load_profile, name="load_profile"),
]
