from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services.dashboard_filters import DashboardFilters
from .services.dashboard_queries import get_dashboard_context


@login_required
def dashboard_home(request):
    filters = DashboardFilters.from_querydict(request.GET)
    context = get_dashboard_context(filters)
    return render(request, "dashboard/home.html", context)
