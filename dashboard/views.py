from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services.dashboard_queries import get_dashboard_placeholder


@login_required
def dashboard_home(request):
    context = get_dashboard_placeholder()
    return render(request, "dashboard/home.html", context)
