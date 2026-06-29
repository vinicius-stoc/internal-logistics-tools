from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("export/excel/", views.export_dashboard_excel, name="export_excel"),
]
