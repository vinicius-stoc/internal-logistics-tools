from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse

from accounts.services.user_service import get_user_profile


def password_change_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = get_user_profile(request.user)
            force_change_url = reverse("accounts:force_password_change")

            if profile.must_change_password and request.path != force_change_url:
                return redirect(force_change_url)

        return view_func(request, *args, **kwargs)

    return wrapper
