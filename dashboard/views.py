from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from accounts.decorators import password_change_required

from .services.dashboard_filters import DashboardFilters
from .services.dashboard_queries import get_dashboard_context


@login_required
@password_change_required
@permission_required("accounts.access_dashboard", raise_exception=True)
def dashboard_home(request):
    filters = DashboardFilters.from_querydict(request.GET)
    context = get_dashboard_context(filters)
    return render(request, "dashboard/home.html", context)
