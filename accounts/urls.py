from django.urls import include, path

from . import views


app_name = "accounts"

urlpatterns = [
    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:user_id>/toggle-active/", views.user_toggle_active, name="user_toggle_active"),
    path("users/<int:user_id>/reset-password/", views.user_reset_password, name="user_reset_password"),
    path("password/force-change/", views.force_password_change, name="force_password_change"),
    path("", include("django.contrib.auth.urls")),
]
