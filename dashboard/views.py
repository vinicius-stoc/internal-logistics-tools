from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.decorators import password_change_required

from .services.dashboard_filters import DashboardFilters
from .services.dashboard_queries import get_dashboard_context
from .services.export_service import DashboardExportError, build_dashboard_export


@login_required
@password_change_required
@permission_required("accounts.access_dashboard", raise_exception=True)
def dashboard_home(request):
    filters = DashboardFilters.from_querydict(request.GET)
    context = get_dashboard_context(filters, request.GET)
    return render(request, "dashboard/home.html", context)


@login_required
@password_change_required
@permission_required("accounts.export_dashboard", raise_exception=True)
def export_dashboard_excel(request):
    filters = DashboardFilters.from_querydict(request.GET)

    try:
        export_result = build_dashboard_export(filters)
    except DashboardExportError:
        messages.error(
            request,
            "Nao foi possivel gerar a exportacao Excel. Tente novamente ou ajuste os filtros.",
        )
        return redirect(_dashboard_url_with_querystring(request))

    response = HttpResponse(export_result.content, content_type=export_result.content_type)
    response["Content-Disposition"] = f'attachment; filename="{export_result.file_name}"'
    return response


def _dashboard_url_with_querystring(request):
    dashboard_url = reverse("dashboard:home")
    querystring = request.GET.urlencode()
    if querystring:
        return f"{dashboard_url}?{querystring}"
    return dashboard_url
