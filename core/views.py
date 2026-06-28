from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.decorators import password_change_required


@login_required
@password_change_required
def home(request):
    return render(request, "core/home.html")
